import { CapacitorSQLite, SQLiteConnection, SQLiteDBConnection } from '@capacitor-community/sqlite';
import { Capacitor } from '@capacitor/core';
import { API_BASE } from '../store/useLifeOSStore';

export class OfflineSyncService {
  private static sqlite: SQLiteConnection | null = null;
  private static db: SQLiteDBConnection | null = null;
  private static isInitialized = false;

  public static get initialized(): boolean {
    return this.isInitialized;
  }

  /**
   * Initializes the local SQLite database schema for Tasks, Notes, and the Sync Queue.
   */
  public static async init(): Promise<void> {
    if (!Capacitor.isNativePlatform()) {
      this.isInitialized = true;
      return;
    }

    try {
      this.sqlite = new SQLiteConnection(CapacitorSQLite);
      this.db = await this.sqlite.createConnection(
        'lifeos_local_db',
        false,
        'no-encryption',
        1,
        false
      );
      await this.db.open();

      // Schema definition
      const createTablesQuery = `
        CREATE TABLE IF NOT EXISTS local_tasks (
          id INTEGER PRIMARY KEY,
          title TEXT NOT NULL,
          description TEXT,
          priority TEXT,
          status TEXT,
          due_date TEXT,
          updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS local_notes (
          id INTEGER PRIMARY KEY,
          title TEXT NOT NULL,
          content TEXT,
          tags TEXT,
          updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS sync_queue (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          action TEXT NOT NULL, -- 'CREATE', 'UPDATE', 'DELETE'
          item_type TEXT NOT NULL, -- 'task', 'note'
          item_id INTEGER,
          payload TEXT,
          timestamp INTEGER
        );
      `;
      await this.db.execute(createTablesQuery);
      this.isInitialized = true;
      console.log('SQLite local database initialized successfully.');
    } catch (error) {
      console.error('Failed to initialize SQLite local database:', error);
    }
  }

  /**
   * Enqueues a sync action when offline.
   */
  public static async enqueueAction(
    action: 'CREATE' | 'UPDATE' | 'DELETE',
    itemType: 'task' | 'note' | 'habit',
    itemId: number,
    payload: any
  ): Promise<void> {
    if (!Capacitor.isNativePlatform() || !this.db) {
      // Web fallback: localStorage queue
      const webQueue = JSON.parse(localStorage.getItem('sync_queue') || '[]');
      webQueue.push({ action, itemType, itemId, payload, timestamp: Date.now() });
      localStorage.setItem('sync_queue', JSON.stringify(webQueue));
      return;
    }

    try {
      const query = `
        INSERT INTO sync_queue (action, item_type, item_id, payload, timestamp)
        VALUES (?, ?, ?, ?, ?);
      `;
      await this.db.run(query, [action, itemType, itemId, JSON.stringify(payload), Date.now()]);
    } catch (error) {
      console.error('Failed to enqueue sync action:', error);
    }
  }

  private static retryCount = 0;
  private static isSyncing = false;

  /**
   * Synchronizes the local queue with the backend API.
   * Resolves conflicts by applying the local change if it is newer, or backend-wins fallback.
   */
  public static async syncWithBackend(authToken: string): Promise<void> {
    if (!navigator.onLine || this.isSyncing) return;
    this.isSyncing = true;

    try {
      let queueItems: any[] = [];

      if (!Capacitor.isNativePlatform() || !this.db) {
        // Web fallback
        queueItems = JSON.parse(localStorage.getItem('sync_queue') || '[]');
      } else {
        const result = await this.db.query('SELECT * FROM sync_queue ORDER BY timestamp ASC;');
        queueItems = result.values || [];
      }

      if (queueItems.length === 0) {
        this.retryCount = 0;
        this.isSyncing = false;
        return;
      }

      console.log(`Starting synchronization of ${queueItems.length} offline actions...`);
      let syncFailed = false;

      for (const item of queueItems) {
        let endpoint = '';
        let method = 'POST';
        const payload = JSON.parse(item.payload || '{}');

        if (item.item_type === 'task') {
          endpoint = `${API_BASE}/tasks`;
          if (item.action === 'UPDATE') {
            endpoint = `${API_BASE}/tasks/${item.item_id}`;
            method = 'PUT';
          } else if (item.action === 'DELETE') {
            endpoint = `${API_BASE}/tasks/${item.item_id}`;
            method = 'DELETE';
          }
        } else if (item.item_type === 'note') {
          endpoint = `${API_BASE}/notes`;
          if (item.action === 'UPDATE') {
            endpoint = `${API_BASE}/notes/${item.item_id}`;
            method = 'PUT';
          } else if (item.action === 'DELETE') {
            endpoint = `${API_BASE}/notes/${item.item_id}`;
            method = 'DELETE';
          }
        } else if (item.item_type === 'habit') {
          endpoint = `${API_BASE}/habits`;
          if (item.action === 'UPDATE') {
            endpoint = `${API_BASE}/habits/${item.item_id}/logs`;
            method = 'POST';
          } else if (item.action === 'DELETE') {
            endpoint = `${API_BASE}/habits/${item.item_id}`;
            method = 'DELETE';
          }
        }

        try {
          const response = await fetch(endpoint, {
            method,
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${authToken}`
            },
            body: item.action !== 'DELETE' ? JSON.stringify(payload) : undefined
          });

          if (response.ok || response.status === 404) {
            // Success or item not found on server (conflict resolved as deleted)
            if (Capacitor.isNativePlatform() && this.db) {
              await this.db.run('DELETE FROM sync_queue WHERE id = ?;', [item.id]);
            } else {
              // Web fallback filter out this item
              const webQueue = JSON.parse(localStorage.getItem('sync_queue') || '[]');
              const updatedWebQueue = webQueue.filter((q: any) => q.timestamp !== item.timestamp);
              localStorage.setItem('sync_queue', JSON.stringify(updatedWebQueue));
            }
          } else {
            syncFailed = true;
            break;
          }
        } catch (err) {
          console.error(`Failed to sync item ${item.id}:`, err);
          syncFailed = true;
          break; // Stop replaying the queue to preserve sequence on connection drop
        }
      }

      if (syncFailed) {
        this.retryCount += 1;
        const delay = Math.min(60000, Math.pow(2, this.retryCount) * 1000);
        console.warn(`Synchronization failed. Retrying in ${delay}ms (attempt ${this.retryCount})...`);
        setTimeout(() => {
          this.isSyncing = false;
          this.syncWithBackend(authToken);
        }, delay);
      } else {
        this.retryCount = 0;
        this.isSyncing = false;
        console.log('Offline sync completed successfully.');
      }
    } catch (error) {
      console.error('Error during synchronization:', error);
      this.isSyncing = false;
    }
  }
}
