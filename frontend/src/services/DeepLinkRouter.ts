import { useLifeOSStore } from '../store/useLifeOSStore';

export class DeepLinkRouter {
  private static routes: Record<string, string> = {
    '/tasks': 'tasks',
    '/ai': 'ai_assistant',
    '/dashboard': 'dashboard',
    '/panchang': 'calendar_agenda',
    '/trading': 'trading',
    '/notes': 'notes'
  };

  /**
   * Route deep links to the appropriate tab screen.
   */
  public static handleUrl(urlStr: string): void {
    console.log('DeepLinkRouter processing URL:', urlStr);
    try {
      let path = '';
      if (urlStr.includes('://')) {
        const urlParts = urlStr.split('://');
        const pathPart = urlParts[1] || '';
        // If it starts with app/, remove it
        if (pathPart.startsWith('app/')) {
          path = '/' + pathPart.substring(4);
        } else {
          path = '/' + pathPart;
        }
      } else {
        // Assume HTTP/HTTPS url
        const url = new URL(urlStr);
        path = url.pathname;
      }

      // Remove trailing slash if present
      if (path.endsWith('/') && path.length > 1) {
        path = path.slice(0, -1);
      }

      const store = useLifeOSStore.getState();
      const targetTab = this.routes[path];

      if (targetTab) {
        console.log(`DeepLinkRouter: routing path "${path}" to tab "${targetTab}"`);
        store.setActiveTab(targetTab);
      } else {
        console.warn(`DeepLinkRouter: unknown path "${path}". Falling back to dashboard.`);
        store.setActiveTab('dashboard');
      }
    } catch (error) {
      console.error('DeepLinkRouter error parsing URL:', error);
      const store = useLifeOSStore.getState();
      store.setActiveTab('dashboard');
    }
  }
}
