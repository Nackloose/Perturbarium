# Cross-Platform Monorepo Architecture Rulebook
## Universal Frontend Framework Deployables

**Version:** 3.0  
**Purpose:** Definitive guide for building maintainable, scalable cross-platform monorepos with any frontend framework  
**Philosophy:** Single codebase, multiple deployment targets, maximum code reuse  
**Framework Agnostic:** Supports React, Vue, Svelte, Angular, or any Vite-compatible framework

---

## 📝 **Important Note: Framework Examples**

**This rulebook uses React for demonstration purposes throughout the examples.**  
**Substitute with your preferred framework (Vue, Svelte, Angular, etc.) as desired.**

### **Framework Substitution Guide:**
- **React examples** → Replace with your chosen framework
- **JSX syntax** → Use your framework's template syntax
- **React hooks** → Use your framework's reactivity system
- **React components** → Use your framework's component system

### **Example Substitutions:**
```typescript
// React (demonstration)
const App = () => <div>Hello React</div>;

// Vue equivalent
const App = { template: '<div>Hello Vue</div>' };

// Svelte equivalent  
const App = { template: '<div>Hello Svelte</div>' };

// Angular equivalent
@Component({ template: '<div>Hello Angular</div>' })
class App { }
```

**All architectural patterns, build systems, and deployment strategies remain identical regardless of framework choice.**  

---

## 🏛️ Core Architecture Principles

### **1. Core-First Philosophy**
- **Business logic belongs in core packages** - Never duplicate core functionality
- **Shared code is for cross-cutting concerns** - Utilities, types, and services used by multiple packages
- **UI components should be platform-agnostic** - Abstract platform differences through props
- **Types are the contract** - TypeScript interfaces define the communication layer
- **Platform-specific code is injected** - Dependency injection over conditional compilation
- **Framework agnostic** - Core packages work with any frontend framework (React, Vue, Svelte, Angular, etc.)

### **2. Separation of Concerns**
```
├── packages/          # Shared libraries (utilities, types, cross-cutting concerns)
├── apps/             # Platform-specific applications (deployment targets)
└── data/            # Shared development data
```

### **3. Progressive Enhancement**
- **Start with web capabilities** - Lowest common denominator
- **Enhance with platform features** - Add native capabilities through bridges
- **Graceful degradation** - Handle missing features elegantly
- **Feature detection over platform detection** - Check capabilities, not environment
- **Framework flexibility** - Choose any frontend framework that works with Vite

### **4. Unified Server Architecture** 
- **Single port for all services** - Backend API and frontend served from same port
- **Intelligent request routing** - API routes handled by server, everything else proxied to Vite
- **WebSocket multiplexing** - Both application and HMR WebSockets on same connection
- **Environment parity** - Development and production use identical routing logic
- **Seamless integration** - No CORS issues, no port juggling, no configuration complexity

**Why Unified Architecture Solves Development Issues:**

The unified server architecture directly addresses the complex overhead and error-prone nature of traditional multi-server development setups. When using Vite with Electron, Capacitor, or other bundling tools, developers face persistent CORS issues, port management complexity, and configuration overhead that creates friction in the development workflow.

By serving both the backend API and frontend from a single port, we eliminate the need for complex proxy configurations, CORS headers, and cross-origin request handling. This unified approach means that desktop applications can leverage local backend services without the network complexity that typically introduces errors in user spaces.

The architecture provides a seamless development experience where the same routing logic used in production is mirrored in development, ensuring that what works locally will work when deployed. This eliminates the "works on my machine" problems that arise from environment differences between development and production setups.

---

## 📁 Directory Structure Template

```
project-root/
├── package.json                 # Workspace configuration
├── tsconfig.json               # Base TypeScript config
├── .gitignore                  # Workspace-wide ignores
├── 
├── packages/                   # Shared libraries
│   ├── core/                   # Core business logic
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── src/
│   │   │   ├── index.ts        # Main export
│   │   │   ├── types/          # TypeScript interfaces
│   │   │   ├── services/       # Business logic services
│   │   │   └── utils/          # Utility functions
│   │   └── dist/               # Built output
│   │
│   ├── shared/                 # Cross-cutting concerns (utilities, types, services)
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── src/
│   │   │   ├── index.ts        # Main export
│   │   │   ├── types/          # Shared types
│   │   │   ├── utils/          # Shared utilities
│   │   │   └── services/       # Shared services
│   │   └── dist/               # Built output
│   │
│   └── ui/                     # Shared UI components
│       ├── package.json
│       ├── tsconfig.json
│       ├── src/
│       │   ├── index.ts        # Component exports
│       │   ├── components/     # React components
│       │   ├── hooks/          # Custom hooks
│       │   └── styles/         # Shared styles
│       └── dist/               # Built output
│
└──  apps/                       # Platform applications
   ├── client/                 # Vite client application
   │   ├── package.json
   │   ├── vite.config.ts
   │   └── src/
   │
   ├── desktop/                # Electron application
   │   ├── package.json
   │   ├── src/
   │   │   ├── main/           # Electron main process
   │   │   └── renderer/       # Electron renderer (uses client build)
   │   └── dist/
   │
   ├── mobile/                 # Capacitor mobile application
   │   ├── package.json
   │   ├── capacitor.config.ts
   │   └── src/                # Capacitor-specific code (uses client build)
   │
   └── backend/                # API server (if needed)
       ├── package.json
       ├── tsconfig.json
       └── src/

### **Modular Deployment Architecture**

While the unified server architecture provides a streamlined development experience, the system is designed to support modular deployments that expose different functionality subsets from the same shared codebase. This allows teams to build specialized applications that draw from the same packages but serve different purposes.

**Custom Deployment Integration:**

The architecture supports easy addition of custom deployments that build and expose specific subsets of features and functions. For example, you could create:

- **CLI applications** that expose command-line functionality using the same business logic packages
- **GUI applications** that provide desktop interfaces with full server capabilities
- **Server-CLI hybrids** that combine server functionality with command-line interfaces but no GUI
- **API-only servers** that build isolated API endpoints drawing from the shared packages
- **Headless services** that run background processes using the same core logic

All these deployment targets would build from the same shared packages (`packages/shared`, `packages/ui`, etc.) but expose different interfaces and functionality subsets. This modular approach enables teams to create specialized applications for different use cases while maintaining code consistency and reducing duplication.

The architecture maintains the unified development experience while providing flexibility to deploy applications that serve specific purposes - whether that's a CLI tool for developers, a GUI for end users, or an API server for integration - all built from the same foundational codebase.

---

## 📦 Package Configuration Patterns

### **Root Package.json Template**
```json
{
  "name": "your-project",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "packages/*",
    "apps/*"
  ],
  "scripts": {
    "dev": "npm run dev --workspace=@yourproject/backend",
    "dev:desktop": "npm run dev --workspace=@yourproject/desktop",
    "dev:client": "npm run dev --workspace=@yourproject/client",
    "dev:mobile": "npm run dev --workspace=@yourproject/mobile",
    "build": "npm run build:core && npm run build:shared && npm run build:ui && npm run build:client && npm run build:desktop && npm run build:mobile",
    "build:core": "npm run build --workspace=@yourproject/core",
    "build:shared": "npm run build --workspace=@yourproject/shared",
    "build:ui": "npm run build --workspace=@yourproject/ui",
    "build:client": "npm run build --workspace=@yourproject/client",
    "build:desktop": "npm run build --workspace=@yourproject/desktop",
    "build:mobile": "npm run sync --workspace=@yourproject/mobile",
    "type-check": "npm run type-check --workspace=@yourproject/shared && npm run type-check --workspace=@yourproject/ui && npm run type-check --workspace=@yourproject/backend && npm run type-check --workspace=@yourproject/desktop && npm run type-check --workspace=@yourproject/mobile",
    "clean": "npm run clean --workspace=@yourproject/shared && npm run clean --workspace=@yourproject/ui && npm run clean --workspace=@yourproject/backend && npm run clean --workspace=@yourproject/desktop && npm run clean --workspace=@yourproject/mobile",
    "mobile:ios": "npm run ios --workspace=@yourproject/mobile",
    "mobile:android": "npm run android --workspace=@yourproject/mobile",
    "mobile:sync": "npm run sync --workspace=@yourproject/mobile"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0",
    "concurrently": "^8.2.0"
  }
}
```

### **Core Package Template**
```json
{
  "name": "@yourproject/core",
  "version": "1.0.0",
  "private": true,
  "description": "Core business logic and application services",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": ["dist"],
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "type-check": "tsc --noEmit",
    "clean": "rm -rf dist"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0"
  },
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "default": "./dist/index.js"
    },
    "./types": {
      "types": "./dist/types/index.d.ts",
      "default": "./dist/types/index.js"
    },
    "./utils": {
      "types": "./dist/utils/index.d.ts", 
      "default": "./dist/utils/index.js"
    },
    "./services": {
      "types": "./dist/services/index.d.ts",
      "default": "./dist/services/index.js"
    }
  }
}
```

### **Shared Package Template**
```json
{
  "name": "@yourproject/shared",
  "version": "1.0.0",
  "private": true,
  "description": "Shared types, utilities, and cross-cutting concerns",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": ["dist"],
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "type-check": "tsc --noEmit",
    "clean": "rm -rf dist"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0"
  },
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "default": "./dist/index.js"
    },
    "./types": {
      "types": "./dist/types/index.d.ts",
      "default": "./dist/types/index.js"
    },
    "./utils": {
      "types": "./dist/utils/index.d.ts", 
      "default": "./dist/utils/index.js"
    },
    "./services": {
      "types": "./dist/services/index.d.ts",
      "default": "./dist/services/index.js"
    }
  }
}
```

### **UI Package Template**
```json
{
  "name": "@yourproject/ui",
  "version": "1.0.0",
  "private": true,
  "description": "Shared UI components",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "files": ["dist"],
  "scripts": {
    "build": "tsc && cp -r src/styles dist/",
    "dev": "tsc --watch",
    "type-check": "tsc --noEmit",
    "clean": "rm -rf dist"
  },
  "dependencies": {
    "@yourproject/core": "*",
    "@yourproject/shared": "*",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0"
  },
  "peerDependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "default": "./dist/index.js"
    },
    "./styles": {
      "default": "./dist/styles/index.css"
    }
  }
}
```

---

## 🔧 TypeScript Configuration Strategy

### **Base TypeScript Config (Root)**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowJs": true,
    "checkJs": false,
    "jsx": "react-jsx",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "removeComments": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitReturns": true,
    "noImplicitThis": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "isolatedModules": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts", "**/*.test.tsx"]
}
```

### **Shared Package TypeScript Config**
```json
{
  "extends": "../../tsconfig.json",
  "compilerOptions": {
    "module": "CommonJS",
    "target": "ES2020",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./"
  },
  "include": ["**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules", "dist"]
}
```

### **App-Specific TypeScript Config**
```json
{
  "extends": "../../tsconfig.json",
  "compilerOptions": {
    "module": "ESNext",
    "target": "ES2020",
    "noEmit": false,
    "declaration": false,
    "jsx": "react-jsx"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

---

## 🌉 Platform Bridge Architecture

### **Core Bridge Interface**
```typescript
// packages/core/services/platform-bridge.ts
export interface PlatformBridge {
  // Platform identification
  getPlatformType(): 'web' | 'desktop' | 'mobile';
  getPlatformInfo(): Promise<PlatformInfo>;
  
  // Universal capabilities
  isOnline(): Promise<boolean>;
  showNotification(title: string, message: string, options?: NotificationOptions): Promise<void>;
  
  // Feature detection
  hasFeature(feature: string): boolean;
}

export interface PlatformInfo {
  platform: string;
  version: string;
  userAgent?: string;
}

export interface NotificationOptions {
  icon?: string;
  sound?: boolean;
  urgent?: boolean;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  id: string;
  title: string;
  callback: () => void;
}
```

### **Platform-Specific Extensions**
```typescript
// Desktop-specific bridge
export interface DesktopPlatformBridge extends PlatformBridge {
  selectFolder(): Promise<string | null>;
  openFile(path: string): Promise<void>;
  showInFolder(path: string): Promise<void>;
  showSaveDialog(options?: SaveDialogOptions): Promise<string | null>;
  setAutoStart(enabled: boolean): Promise<void>;
}

// Browser-specific bridge
export interface BrowserPlatformBridge extends PlatformBridge {
  requestFullscreen(): Promise<void>;
  requestPersistentStorage(): Promise<boolean>;
  isFileSystemAccessSupported(): boolean;
}

// Mobile-specific bridge
export interface MobilePlatformBridge extends PlatformBridge {
  requestPermissions(permissions: string[]): Promise<Record<string, boolean>>;
}
```

---

## 🏗️ Build System Patterns

### **Seamless Vite-Backend Integration**

The most elegant monorepo pattern is to integrate the Vite dev server directly into your backend server, eliminating the need for separate ports and CORS configuration. This creates a single-port development experience identical to production.

#### **Backend Server with Embedded Vite**
```typescript
// server/src/index.ts
import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { spawn, ChildProcess } from 'child_process';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import path from 'path';

class UnifiedServer {
  private app: express.Application;
  private server: ReturnType<typeof createServer> | null = null;
  private viteProcess: ChildProcess | null = null;
  private vitePort: number = 0;
  private viteProxy: ReturnType<typeof createProxyMiddleware> | null = null;
  private wsServer: WebSocketServer | null = null;

  constructor(private config: {
    port: number;
    mode: 'development' | 'production';
    projectRoot: string;
  }) {
    this.app = express();
    this.setupMiddleware();
  }

  private setupMiddleware(): void {
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));

    // Health check endpoint
    this.app.get('/health', (req, res) => {
      res.json({ 
        status: 'ok', 
        mode: this.config.mode,
        vitePort: this.vitePort 
      });
    });
  }

  private async startViteServer(): Promise<number> {
    if (this.config.mode === 'production') {
      return 0; // No Vite server needed in production
    }

    const vitePort = await this.findAvailablePort();
    this.vitePort = vitePort;

    return new Promise((resolve, reject) => {
      const frontendPath = path.resolve(__dirname, '../../frontend');
      
      this.viteProcess = spawn('npx', [
        'vite',
        '--port', vitePort.toString(),
        '--host', '127.0.0.1',
        '--strictPort'
      ], {
        cwd: frontendPath,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, FORCE_COLOR: '1' }
      });

      const onData = (data: Buffer) => {
        const output = data.toString();
        console.log(`[Vite] ${output}`);

        if (output.includes('Local:') || output.includes('ready in')) {
          console.log(`✅ Vite dev server started on port ${vitePort}`);
          resolve(vitePort);
        }
      };

      this.viteProcess.stdout?.on('data', onData);
      this.viteProcess.stderr?.on('data', onData);
      this.viteProcess.on('error', reject);

      // Timeout after 30 seconds
      setTimeout(() => reject(new Error('Vite startup timeout')), 30000);
    });
  }

  private setupViteProxy(): void {
    if (this.config.mode === 'production') {
      // Serve built frontend files directly
      const frontendBuildPath = path.resolve(__dirname, '../../frontend/dist');
      this.app.use(express.static(frontendBuildPath));
      return;
    }

    // Create proxy for all non-API requests
    this.viteProxy = createProxyMiddleware({
      target: `http://127.0.0.1:${this.vitePort}`,
      changeOrigin: true,
      ws: false, // Handle WebSocket upgrades manually
      logLevel: 'silent',
      onError: (err, req, res) => {
        console.error('Vite proxy error:', err.message);
        if (res && !res.headersSent) {
          res.status(500).json({ error: 'Vite server connection failed' });
        }
      },
    });

    // CRITICAL: Apply proxy to all non-API routes
    this.app.use((req, res, next) => {
      if (req.path.startsWith('/api/')) {
        next(); // Let API routes handle it
      } else {
        this.viteProxy!(req, res, next); // Proxy to Vite
      }
    });
  }

  private setupAPIRoutes(): void {
    // Mount API routes BEFORE the Vite proxy
    this.app.use('/api', createApiRouter());
    
    // API routes are now available at /api/*
    // Everything else will be proxied to Vite
  }

  private setupWebSocketRouting(): void {
    // Handle WebSocket upgrades intelligently
    this.server!.on('upgrade', (req, socket, head) => {
      const pathname = req.url || '';

      if (pathname === '/api/ws') {
        // Handle API WebSocket connections
        this.wsServer!.handleUpgrade(req, socket, head, (ws) => {
          this.wsServer!.emit('connection', ws, req);
        });
      } else if (this.config.mode === 'development' && this.viteProxy) {
        // Proxy Vite HMR WebSocket connections
        (this.viteProxy as any).upgrade(req, socket, head);
      } else {
        socket.destroy();
      }
    });
  }

  async start(): Promise<void> {
    console.log(`🚀 Starting unified server in ${this.config.mode} mode...`);
    
    if (this.config.mode === 'development') {
      await this.startViteServer();
    }

    // Order matters: API routes first, then Vite proxy
    this.setupAPIRoutes();
    this.setupViteProxy();

    this.server = createServer(this.app);
    
    // Setup WebSocket server
    this.wsServer = new WebSocketServer({ noServer: true });
    this.setupWebSocketRouting();

    await new Promise<void>((resolve, reject) => {
      this.server!.listen(this.config.port, () => {
        console.log(`✅ Unified server running on http://localhost:${this.config.port}`);
        if (this.config.mode === 'development') {
          console.log(`   ⚡ Vite dev server: http://127.0.0.1:${this.vitePort}`);
          console.log(`   🔄 HMR and WebSockets proxied seamlessly`);
        }
        resolve();
      });
      this.server!.on('error', reject);
    });
  }

  private async findAvailablePort(): Promise<number> {
    // Implementation to find an available port
    return new Promise((resolve) => {
      const server = require('net').createServer();
      server.listen(0, () => {
        const port = server.address().port;
        server.close(() => resolve(port));
      });
    });
  }
}

// Usage
const server = new UnifiedServer({
  port: 3000,
  mode: process.env.NODE_ENV as 'development' | 'production',
  projectRoot: process.cwd()
});

server.start().catch(console.error);
```

#### **Minimal Vite Configuration**
```typescript
// frontend/vite.config.ts - Simplified because proxy is handled by backend
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@core': path.resolve(__dirname, '../core/src'),
      '@shared': path.resolve(__dirname, '../shared/src')
    }
  },
  // No server config needed - backend handles everything
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          core: ['@yourproject/core'],
          shared: ['@yourproject/shared']
        }
      }
    }
  }
});
```

### **Traditional Vite Configuration (Alternative)**

For cases where you need separate servers:

#### **Client App Config**
```typescript
// apps/client/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@core': path.resolve(__dirname, '../../packages/core/src'),
      '@shared': path.resolve(__dirname, '../../packages/shared/src'),
      '@ui': path.resolve(__dirname, '../../packages/ui/src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          core: ['@yourproject/core'],
          shared: ['@yourproject/shared']
        }
      }
    }
  }
});
```

#### **Desktop App Config**
```typescript
// apps/desktop/src/main/index.ts
import { app, BrowserWindow } from 'electron';
import path from 'path';

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load the client build
  if (process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../../client/dist/index.html'));
  }
}

app.whenReady().then(createWindow);
```

```json
// apps/desktop/package.json
{
  "name": "@yourproject/desktop",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "electron .",
    "build": "tsc",
    "start": "electron .",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "@yourproject/core": "*",
    "@yourproject/shared": "*",
    "electron": "^25.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0"
  }
}
```

### **Electron Configuration**
```json
// apps/desktop/package.json (build section)
{
  "build": {
    "appId": "com.yourcompany.yourapp",
    "productName": "Your App",
    "directories": {
      "output": "release"
    },
    "files": [
      "dist/**/*",
      "node_modules/**/*",
      "!node_modules/.cache"
    ],
    "mac": {
      "category": "public.app-category.productivity",
      "icon": "assets/icon.icns"
    },
    "win": {
      "target": "nsis",
      "icon": "assets/icon.ico"
    },
    "linux": {
      "target": "AppImage",
      "category": "Utility",
      "icon": "assets/icon.png"
    }
  }
}
```

### **Capacitor Mobile Configuration**
```typescript
// apps/mobile/capacitor.config.ts
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.yourcompany.yourapp',
  appName: 'Your App',
  webDir: '../client/dist', // Points to client build
  server: {
    androidScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: "#ffffffff",
      androidSplashResourceName: "splash",
      androidScaleType: "CENTER_CROP",
      showSpinner: true,
      androidSpinnerStyle: "large",
      iosSpinnerStyle: "small",
      spinnerColor: "#999999",
      splashFullScreen: true,
      splashImmersive: true,
      layoutName: "launch_screen",
      useDialog: true,
    },
    Notifications: {
      iconColor: "#488AFF",
      sound: "beep.wav",
    }
  }
};

export default config;
```

```json
// apps/mobile/package.json
{
  "name": "@yourproject/mobile",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "sync": "npx cap sync",
    "ios": "npx cap run ios",
    "android": "npx cap run android",
    "build:ios": "npx cap build ios",
    "build:android": "npx cap build android",
    "type-check": "tsc --noEmit",
    "clean": "rm -rf dist"
  },
  "dependencies": {
    "@yourproject/core": "*",
    "@yourproject/shared": "*",
    "@yourproject/ui": "*",
    "@capacitor/core": "^5.0.0",
    "@capacitor/ios": "^5.0.0",
    "@capacitor/android": "^5.0.0",
    "@capacitor/app": "^5.0.0",
    "@capacitor/device": "^5.0.0",
    "@capacitor/notifications": "^5.0.0",
    "@capacitor/storage": "^5.0.0",
    "@capacitor/filesystem": "^5.0.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0"
  }
}
```



---

## 🎯 Component Architecture Patterns

### **Universal Component Template**
```typescript
// packages/ui/src/components/App.tsx
import React from 'react';
import type { PlatformBridge } from '@yourproject/core';

interface AppProps {
  // Platform capabilities injected as props
  platformBridge?: PlatformBridge;
  
  // Configuration
  apiUrl?: string;
  theme?: 'light' | 'dark';
  
  // Event handlers
  onError?: (error: Error) => void;
}

export const App: React.FC<AppProps> = ({ 
  platformBridge,
  apiUrl = 'http://localhost:3001',
  theme = 'light',
  onError
}) => {
  // Feature detection
  const hasNativeFeatures = !!platformBridge;
  
  // Conditional behavior based on platform capabilities
  const handleAction = async () => {
    if (platformBridge?.hasFeature('file-system')) {
      await platformBridge.selectFolder();
    } else {
      // Web fallback
      const input = document.createElement('input');
      input.type = 'file';
      input.webkitdirectory = true;
      input.click();
    }
  };

  return (
    <div className={`app app--${theme}`}>
      {/* Universal UI */}
      <button onClick={handleAction}>
        {hasNativeFeatures ? 'Select Folder' : 'Upload Files'}
      </button>
    </div>
  );
};
```

### **Platform-Specific Implementations**

#### **Desktop Implementation**
```typescript
// apps/desktop/src/renderer/App.tsx
import React, { useEffect, useState } from 'react';
import { App as SharedApp } from '@yourproject/ui';
import type { DesktopPlatformBridge } from '@yourproject/core';

const desktopBridge: DesktopPlatformBridge = {
  getPlatformType: () => 'desktop',
  getPlatformInfo: async () => ({
    platform: 'desktop',
    version: await window.electronAPI.getVersion()
  }),
  hasFeature: (feature: string) => {
    const features = ['file-system', 'notifications', 'auto-start'];
    return features.includes(feature);
  },
  selectFolder: async () => {
    return await window.electronAPI.selectFolder();
  },
  openFile: async (path: string) => {
    await window.electronAPI.openFile(path);
  }
};

export const DesktopApp: React.FC = () => {
  return (
    <SharedApp 
      platformBridge={desktopBridge}
      apiUrl="http://localhost:3001"
    />
  );
};
```

#### **Client Implementation**
```typescript
// apps/client/src/App.tsx
import React from 'react';
import { App as SharedApp } from '@yourproject/ui';
import type { BrowserPlatformBridge } from '@yourproject/core';

const clientBridge: BrowserPlatformBridge = {
  getPlatformType: () => 'web',
  getPlatformInfo: async () => ({
    platform: 'web',
    version: '1.0.0',
    userAgent: navigator.userAgent
  }),
  hasFeature: (feature: string) => {
    const features = ['notifications'];
    if (feature === 'file-system') {
      return 'showDirectoryPicker' in window;
    }
    return features.includes(feature);
  },
  requestFullscreen: async () => {
    await document.documentElement.requestFullscreen();
  },
  requestPersistentStorage: async () => {
    const result = await navigator.storage.persist();
    return result;
  }
};

export const ClientApp: React.FC = () => {
  return (
    <SharedApp 
      platformBridge={clientBridge}
      apiUrl="/api"
    />
  );
};
```

#### **Mobile Implementation**
```typescript
// apps/mobile/src/App.tsx
import React from 'react';
import { App as SharedApp } from '@yourproject/ui';
import type { MobilePlatformBridge } from '@yourproject/core';
import { Capacitor } from '@capacitor/core';
import { Device } from '@capacitor/device';
import { Notifications } from '@capacitor/notifications';
import { App } from '@capacitor/app';

const mobileBridge: MobilePlatformBridge = {
  getPlatformType: () => 'mobile',
  getPlatformInfo: async () => {
    const info = await Device.getInfo();
    return {
      platform: info.platform,
      version: info.osVersion,
      userAgent: navigator.userAgent
    };
  },
  hasFeature: (feature: string) => {
    const features = ['notifications', 'permissions'];
    return features.includes(feature);
  },
  isOnline: async () => {
    return navigator.onLine;
  },
  showNotification: async (title: string, message: string) => {
    await Notifications.schedule({
      notifications: [
        {
          title,
          body: message,
          id: Date.now().toString(),
          schedule: { at: new Date(Date.now() + 1000) }
        }
      ]
    });
  },
  requestPermissions: async (permissions: string[]) => {
    const results: Record<string, boolean> = {};
    
    for (const permission of permissions) {
      if (permission === 'notifications') {
        const result = await Notifications.requestPermissions();
        results[permission] = result.display === 'granted';
      } else {
        // Handle other permissions as needed
        results[permission] = true;
      }
    }
    
    return results;
  },

};

export const MobileApp: React.FC = () => {
  return (
    <SharedApp 
      platformBridge={mobileBridge}
      apiUrl="https://your-api-server.com"
    />
  );
};
```

---

## 🔄 Development Workflow

### **Unified Development Workflow**

With the seamless Vite-backend integration, the development workflow becomes incredibly simple:

#### **Development Commands**
```bash
# Single command to start everything
npm run dev                    # Starts unified server with embedded Vite

# Build process
npm run build                 # Build all packages and apps
npm run build:core            # Build core package only
npm run build:shared          # Build shared packages only
npm run build:frontend        # Build frontend only
npm run build:server          # Build server only

# Type checking
npm run type-check           # Check types across all packages

# Cleaning
npm run clean               # Clean all build artifacts

# Alternative: Traditional separate servers
npm run dev:server           # Start backend server only
npm run dev:frontend         # Start frontend only
npm run dev:all              # Start both with concurrently
```

#### **Package.json Scripts (Unified Approach)**
```json
{
  "scripts": {
    "dev": "npm run dev:shared && npm run dev:server",
    "dev:shared": "npm run build --workspace=@yourproject/shared --watch",
    "dev:server": "npm run dev --workspace=@yourproject/server",
    "dev:all": "concurrently --names \"CORE,SHARED,SERVER\" \"npm run dev:core\" \"npm run dev:shared\" \"npm run dev:server\"",
    "build": "npm run build:core && npm run build:shared && npm run build:frontend && npm run build:server",
    "build:core": "npm run build --workspace=@yourproject/core",
    "build:shared": "npm run build --workspace=@yourproject/shared",
    "build:frontend": "npm run build --workspace=@yourproject/frontend",
    "build:server": "npm run build --workspace=@yourproject/server",
    "start": "npm run start --workspace=@yourproject/server",
    "type-check": "npm run type-check --workspace=@yourproject/core && npm run type-check --workspace=@yourproject/shared && npm run type-check --workspace=@yourproject/server"
  }
}
```

#### **Server Package Scripts**
```json
{
  "name": "@yourproject/server",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc && tsc-alias",
    "start": "node dist/index.js",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "@yourproject/core": "*",
    "@yourproject/shared": "*",
    "express": "^4.18.2",
    "http-proxy-middleware": "^2.0.6",
    "ws": "^8.14.2"
  }
}
```

#### **Frontend Package Scripts**
```json
{
  "name": "@yourproject/frontend",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@yourproject/core": "*",
    "@yourproject/shared": "*",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
```

### **Benefits of Unified Server Architecture**

1. **Single Port Development**: No need to remember multiple ports or deal with CORS
2. **Identical Dev/Prod Experience**: Same routing logic in both environments
3. **Seamless WebSocket Support**: Both API and HMR WebSockets work transparently
4. **Simplified Configuration**: Less configuration files and proxy setup
5. **Fast Development**: No waiting for multiple servers to start
6. **Easy Deployment**: Single server to deploy, serves both API and static files

### **Traditional Development Workflow (Alternative)**

For teams that prefer separate servers:

#### **Development Commands**
```bash
# Start development environment
npm run dev                    # Start main development server
npm run dev:desktop           # Start desktop app in development
npm run dev:client           # Start client app in development
npm run dev:mobile           # Start mobile app in development

# Build process
npm run build                 # Build all packages and apps
npm run build:core            # Build core package only
npm run build:shared          # Build shared packages only
npm run build:ui             # Build UI package only
npm run build:apps           # Build all apps

# Type checking
npm run type-check           # Check types across all packages
npm run type-check:core      # Check core package types
npm run type-check:shared    # Check shared package types
npm run type-check:ui        # Check UI package types

# Cleaning
npm run clean               # Clean all build artifacts

# Mobile-specific commands
npm run mobile:ios           # Run iOS simulator
npm run mobile:android       # Run Android emulator
npm run mobile:build:ios     # Build iOS app
npm run mobile:build:android # Build Android app
```

### **Git Workflow Recommendations**
```bash
# Feature branches
git checkout -b feature/new-platform-support
git checkout -b fix/build-system-issue
git checkout -b refactor/shared-types

# Commit message conventions
feat(core): add new platform bridge interface
feat(shared): add new utility functions
fix(desktop): resolve file selection dialog issue
refactor(ui): extract common hook patterns
build(monorepo): update workspace dependencies
```

---

## 📏 Naming Conventions

### **Package Naming**
```
@yourproject/core            # Core business logic
@yourproject/shared          # Cross-cutting concerns (utilities, types, services)
@yourproject/ui              # UI components
@yourproject/client          # Vite client application
@yourproject/desktop         # Desktop application
@yourproject/mobile          # Mobile application
@yourproject/backend         # Backend API
```

### **File and Directory Naming**
```
kebab-case/                  # Directories
PascalCase.tsx              # React components
camelCase.ts                # TypeScript files
camelCase.test.ts           # Test files
index.ts                    # Entry points
```

### **TypeScript Naming**
```typescript
// interfaces and types
interface PlatformBridge { }
type DeviceType = 'web' | 'desktop' | 'mobile';

// Classes
class SyncEngine { }
abstract class BasePlatformBridge { }

// Constants
const API_BASE_URL = 'http://localhost:3001';
const DEFAULT_CHUNK_SIZE = 1024 * 1024;
```

---

## 🚀 Deployment Strategies

### **Client Deployment**
```bash
# Build client app
npm run build:client

# Deploy to static hosting
npm run deploy:client

# Docker deployment
FROM node:18-alpine
COPY apps/client/dist /usr/share/nginx/html
```

### **Desktop Deployment**
```bash
# Build desktop app
npm run build:desktop

# Create installers
npm run dist:desktop

# Outputs:
# - Windows: .exe installer
# - macOS: .dmg installer  
# - Linux: .AppImage
```

### **Mobile Deployment**
```bash
# Build Capacitor app
npm run build:mobile

# Development builds
npm run mobile:ios           # iOS simulator
npm run mobile:android       # Android emulator

# Production builds
npm run mobile:build:ios     # iOS production build
npm run mobile:build:android # Android production build

# App Store deployment
# iOS: Open Xcode project and archive
# Android: Open Android Studio and build APK/AAB

# Manual deployment
# iOS: Upload to App Store Connect via Xcode
# Android: Upload to Google Play Console via Android Studio

# Testing
npm run mobile:test:ios      # iOS unit tests
npm run mobile:test:android  # Android unit tests
npm run mobile:e2e          # End-to-end tests
```

---

## 🎛️ Configuration Management

### **Environment Variables**
```typescript
// packages/shared/src/config/index.ts
export interface AppConfig {
  apiUrl: string;
  wsUrl: string;
  enableDevMode: boolean;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
}

export const getConfig = (): AppConfig => ({
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:3001',
  wsUrl: process.env.REACT_APP_WS_URL || 'ws://localhost:3001',
  enableDevMode: process.env.NODE_ENV === 'development',
  logLevel: (process.env.REACT_APP_LOG_LEVEL as any) || 'info'
});
```

### **Platform-Specific Configs**
```typescript
// apps/desktop/src/config/desktop.ts
export const desktopConfig = {
  ...getConfig(),
  autoStart: process.env.DESKTOP_AUTO_START === 'true',
  minimizeToTray: process.env.DESKTOP_MINIMIZE_TO_TRAY === 'true',
  dataPath: process.env.DESKTOP_DATA_PATH || '~/Library/Application Support/YourApp'
};

// apps/client/src/config/client.ts  
export const clientConfig = {
  ...getConfig(),
  useServiceWorker: process.env.REACT_APP_USE_SW === 'true',
  enablePWA: process.env.REACT_APP_ENABLE_PWA === 'true'
};

// apps/mobile/src/config/mobile.ts
export const mobileConfig = {
  ...getConfig(),
  enableBackgroundSync: process.env.MOBILE_BACKGROUND_SYNC === 'true',
  syncInterval: parseInt(process.env.MOBILE_SYNC_INTERVAL || '300000'), // 5 minutes
  requestPermissions: process.env.MOBILE_REQUEST_PERMISSIONS === 'true',
  enablePushNotifications: process.env.MOBILE_PUSH_NOTIFICATIONS === 'true',
  batteryOptimized: process.env.MOBILE_BATTERY_OPTIMIZED === 'true'
};
```

---

## 🧪 Testing Strategy

### **Test Structure**
```
packages/shared/
├── src/
│   ├── services/
│   │   ├── sync-engine.ts
│   │   └── sync-engine.test.ts
│   └── types/
│       └── index.test.ts
└── __tests__/
    └── integration/

packages/ui/
├── src/
│   ├── components/
│   │   ├── App.tsx
│   │   └── App.test.tsx
│   └── hooks/
│       ├── useSync.ts
│       └── useSync.test.ts
└── __tests__/
    └── components/
```

### **Test Configuration**
```json
// Root jest.config.js
module.exports = {
  projects: [
    '<rootDir>/packages/shared',
    '<rootDir>/packages/ui',
    '<rootDir>/apps/client',
    '<rootDir>/apps/desktop',
    '<rootDir>/apps/mobile'
  ],
  collectCoverageFrom: [
    'packages/*/src/**/*.{ts,tsx}',
    'apps/*/src/**/*.{ts,tsx}',
    '!**/*.d.ts'
  ]
};
```

---

## 🔍 Troubleshooting Common Issues

### **Workspace Resolution Problems**
```bash
# Clear all node_modules
rm -rf node_modules packages/*/node_modules apps/*/node_modules

# Reinstall dependencies
npm install

# Verify workspace linking
npm ls --workspace=@yourproject/shared
```

### **Build Order Issues**
```bash
# Always build in dependency order
npm run build:shared
npm run build:ui
npm run build:apps
```

### **TypeScript Path Resolution**
```json
// tsconfig.json - Add path mapping
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@yourproject/core": ["packages/core/src"],
      "@yourproject/shared": ["packages/shared/src"],
      "@yourproject/ui": ["packages/ui/src"]
    }
  }
}
```

### **Unified Server Integration Issues**

#### **Vite Server Not Starting**
```bash
# Check if port is available
netstat -tlnp | grep :3000

# Clear Vite cache
rm -rf frontend/node_modules/.vite
rm -rf frontend/dist

# Restart with clean slate
npm run clean && npm run dev
```

#### **API Routes Not Working**
```typescript
// Ensure API routes are mounted BEFORE Vite proxy
private setupRoutes(): void {
  // API routes MUST come first
  this.app.use('/api', apiRouter);
  
  // Vite proxy MUST come after API routes
  this.setupViteProxy();
}

// Check request path debugging
this.app.use((req, res, next) => {
  console.log(`Request: ${req.method} ${req.path}`);
  next();
});
```

#### **WebSocket Connection Issues**
```typescript
// Ensure WebSocket upgrade handling is correct
this.server.on('upgrade', (req, socket, head) => {
  const pathname = req.url || '';
  
  // Debug WebSocket upgrade requests
  console.log(`WebSocket upgrade for: ${pathname}`);
  
  if (pathname === '/api/ws') {
    // Handle API WebSocket
    this.wsServer.handleUpgrade(req, socket, head, (ws) => {
      this.wsServer.emit('connection', ws, req);
    });
  } else if (this.viteProxy) {
    // Proxy to Vite for HMR
    this.viteProxy.upgrade(req, socket, head);
  } else {
    socket.destroy();
  }
});
```

#### **HMR Not Working**
```typescript
// Ensure Vite proxy is configured correctly
this.viteProxy = createProxyMiddleware({
  target: `http://127.0.0.1:${this.vitePort}`,
  changeOrigin: true,
  ws: false, // CRITICAL: Must be false for manual WebSocket handling
  logLevel: 'silent'
});

// Check Vite server is actually running
console.log(`Vite server status: ${this.vitePort}`);
```

---

## 📚 Additional Resources

### **Tools and Libraries**
- **Monorepo Management**: npm workspaces, Lerna, Nx
- **Build Tools**: Vite, Webpack, Rollup
- **Server Integration**: Express, http-proxy-middleware, ws
- **Cross-Platform**: Electron, React Native, Capacitor
- **Testing**: Jest, React Testing Library, Playwright
- **Type Checking**: TypeScript, ESLint, Prettier

### **Best Practices References**
- [React Patterns](https://reactpatterns.com/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Express.js Documentation](https://expressjs.com/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [Electron Best Practices](https://www.electronjs.org/docs/latest/tutorial/security)
- [React Native Guide](https://reactnative.dev/docs/getting-started)

### **Key Architectural Decisions**

#### **Unified Server Benefits**
1. **Developer Experience**: Single command to start everything
2. **No CORS Issues**: Frontend and API share the same origin
3. **WebSocket Simplicity**: Both HMR and app WebSockets work seamlessly
4. **Deployment Simplicity**: Single server to deploy and configure
5. **Environment Consistency**: Development mirrors production exactly
6. **Resource Efficiency**: No duplicate middleware or redundant servers

#### **When to Use Traditional Separate Servers**
- **Large teams**: Different teams managing frontend and backend
- **Microservices**: Multiple backend services with different requirements
- **Complex routing**: Advanced proxy configurations or load balancing
- **Legacy systems**: Existing infrastructure that can't be easily unified

#### **API Route Conventions**
- **All API routes MUST start with `/api/`** - This is the routing contract
- **WebSocket endpoints use `/api/ws`** - Consistent with HTTP API pattern
- **Health checks at `/api/health`** - Standard monitoring endpoint
- **Static assets served from root** - Standard web server behavior

---

**Remember**: This rulebook provides the foundation. Adapt patterns to your specific requirements while maintaining the core architectural principles of separation of concerns, progressive enhancement, unified server architecture, and cross-platform compatibility. 

---

## 🎯 Framework and Build System Selection

### **Framework Agnostic Approach**

This monorepo architecture supports **any frontend framework** that works with Vite. React is no longer a requirement - it's an option alongside Vue, Svelte, Angular, or any other Vite-compatible framework.

**Note:** All examples in this rulebook use React for demonstration purposes. Substitute with your preferred framework as needed.

#### **Supported Frameworks:**
- **React** - Most popular, extensive ecosystem
- **Vue** - Progressive framework, excellent DX
- **Svelte** - Compile-time framework, excellent performance
- **Angular** - Enterprise-grade, TypeScript-first
- **Any Vite-compatible framework**

#### **Framework Selection Criteria:**
```typescript
// All frameworks can use the same core packages
import { useSync } from '@yourproject/core';
import { formatCurrency } from '@yourproject/shared';
import { PlatformBridge } from '@yourproject/types';

// Framework-specific UI components
// React
const ReactApp = () => <div>Hello React</div>;

// Vue
const VueApp = { template: '<div>Hello Vue</div>' };

// Svelte
const SvelteApp = { template: '<div>Hello Svelte</div>' };
```

### **Why Vite + Electron/Capacitor is Optimal**

The **Vite + Electron/Capacitor** approach is the recommended strategy for cross-platform monorepos because it provides maximum code reuse while maintaining excellent performance and development experience across all platforms.

#### **Key Advantages:**

1. **Single Build System**: Vite handles all platforms (web, desktop, mobile)
2. **Maximum Code Reuse**: Same components work everywhere
3. **Unified Development**: Single development workflow
4. **Progressive Enhancement**: Web-first with platform-specific capabilities
5. **Ecosystem Compatibility**: Leverages web ecosystem
6. **Performance**: Good performance across all platforms

#### **Platform Compilation Capabilities:**

| Platform | Vite + Electron/Capacitor | Metro (React Native) | Flutter | Tauri |
|----------|---------------------------|----------------------|---------|-------|
| **Web** | ✅ | ❌ | ✅ | ❌ |
| **Desktop** | ✅ | ❌ | ✅ | ✅ |
| **Mobile** | ✅ | ✅ | ✅ | ❌ |

### **Metro (React Native) Limitations**

**Critical Limitation**: Metro/React Native **cannot compile to web or desktop applications**. This breaks the monorepo's core philosophy of "single codebase, multiple deployment targets."

#### **Metro Platform Support:**
- ✅ **Mobile**: iOS and Android apps
- ❌ **Web**: Cannot compile to web browser
- ❌ **Desktop**: Cannot compile to desktop applications

#### **When Metro Makes Sense:**
- **Mobile-only applications** with no web/desktop requirements
- **Performance-critical mobile apps** requiring native performance
- **Teams with extensive React Native expertise**
- **Applications requiring heavy native API usage**

### **Architecture Benefits of Vite + Electron/Capacitor**

#### **1. Unified Build System**
```typescript
// Only the client needs Vite config
// apps/client/vite.config.ts

export default defineConfig({
  plugins: [react()], // or vue(), svelte(), etc.
  resolve: {
    alias: {
      '@core': path.resolve(__dirname, '../../packages/core/src'),
      '@shared': path.resolve(__dirname, '../../packages/shared/src'),
      '@ui': path.resolve(__dirname, '../../packages/ui/src')
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          core: ['@yourproject/core'],
          shared: ['@yourproject/shared']
        }
      }
    }
  }
});

// Desktop and mobile use the client build
// apps/desktop/src/main/index.ts - Loads client build
// apps/mobile/capacitor.config.ts - Points to client/dist
```

#### **2. Maximum Code Reuse**
```typescript
// packages/ui/src/components/App.tsx - Works everywhere
export const App: React.FC<AppProps> = ({ platformBridge }) => (
  <div className="app">
    {/* Same component, different platform bridges */}
    <button onClick={handleAction}>
      {platformBridge?.hasFeature('file-system') ? 'Select Folder' : 'Upload Files'}
    </button>
  </div>
);

// Framework-specific implementations
// apps/client/src/App.tsx (React)
export const ClientApp = () => <App platformBridge={webBridge} />;

// apps/desktop/src/App.tsx (React + Electron)
export const DesktopApp = () => <App platformBridge={electronBridge} />;

// apps/mobile/src/App.tsx (React + Capacitor)
export const MobileApp = () => <App platformBridge={capacitorBridge} />;
```

#### **3. Progressive Enhancement Pattern**
```typescript
// packages/ui/src/components/FileHandler.tsx
export const FileHandler: React.FC<{ platformBridge?: PlatformBridge }> = ({ 
  platformBridge 
}) => {
  const handleFileAction = async () => {
    if (platformBridge?.hasFeature('file-system')) {
      // Desktop: Native file picker via Electron
      const path = await platformBridge.selectFolder();
    } else if (platformBridge?.hasFeature('file-picker')) {
      // Mobile: Capacitor file picker
      const files = await platformBridge.pickFiles();
    } else {
      // Web: Standard file input
      const input = document.createElement('input');
      input.type = 'file';
      input.click();
    }
  };

  return (
    <button onClick={handleFileAction}>
      {platformBridge?.hasFeature('file-system') ? 'Select Folder' : 'Upload Files'}
    </button>
  );
};
```

### **Development Workflow Comparison**

#### **Vite + Electron/Capacitor Workflow:**
```bash
# Single development command
npm run dev                    # Unified server with embedded Vite

# Platform-specific development
npm run dev:web               # Web development
npm run dev:desktop           # Electron development
npm run dev:mobile            # Capacitor development

# Unified build process
npm run build                 # Build all platforms
npm run build:web            # Build web only
npm run build:desktop        # Build desktop only
npm run build:mobile         # Build mobile only
```

#### **Metro (React Native) Workflow:**
```bash
# Separate development commands
npm run dev:mobile            # Metro development server
npm run dev:web              # Separate webpack development
npm run dev:desktop          # Separate electron development

# Different build systems
npm run build:mobile         # Metro build
npm run build:web           # Webpack build
npm run build:desktop       # Electron build
```

### **Performance Considerations**

#### **Vite + Electron/Capacitor Performance:**
- **Web**: Excellent (native web performance)
- **Desktop**: Good (Electron overhead minimal)
- **Mobile**: Good (Capacitor WebView performance)

#### **Metro Performance:**
- **Web**: Poor (React Native Web overhead)
- **Desktop**: Poor (React Native Web overhead)
- **Mobile**: Excellent (native performance)

### **When to Choose Each Approach**

#### **Choose Vite + Electron/Capacitor when:**
- ✅ Building cross-platform applications
- ✅ Want maximum code reuse
- ✅ Web-first development team
- ✅ Need unified development experience
- ✅ Prioritize development speed
- ✅ Want single build system
- ✅ Using any frontend framework (React, Vue, Svelte, Angular)

#### **Choose Metro (React Native) when:**
- ✅ Building mobile-only applications
- ✅ Need native mobile performance
- ✅ Have extensive native API requirements
- ✅ Team has strong React Native expertise
- ✅ Can accept platform-specific code
- ✅ No web/desktop requirements

#### **Choose Flutter when:**
- ✅ Starting fresh with no existing codebase
- ✅ Need maximum performance across all platforms
- ✅ Have Flutter expertise
- ✅ Want single language (Dart) for everything

### **Migration Strategy**

#### **From Metro to Vite + Electron/Capacitor:**
```typescript
// Step 1: Extract shared logic to packages
// packages/core/src/services/sync-engine.ts
export class SyncEngine {
  // Business logic that works everywhere
}

// Step 2: Create platform-agnostic UI components
// packages/ui/src/components/App.tsx
export const App: React.FC<AppProps> = ({ platformBridge }) => {
  // Universal component that adapts to platform
};

// Step 3: Implement platform-specific bridges
// apps/mobile/src/services/capacitor-bridge.ts
const capacitorBridge: MobilePlatformBridge = {
  // Capacitor-specific implementations
};
```

### **Best Practices for Cross-Platform Development**

#### **1. Feature Detection Over Platform Detection**
```typescript
// ❌ Don't do this
if (platform === 'mobile') {
  // Mobile-specific code
}

// ✅ Do this instead
if (platformBridge?.hasFeature('file-system')) {
  // Use native file system
} else {
  // Use web file input
}
```

#### **2. Progressive Enhancement**
```typescript
// Start with web capabilities, enhance with platform features
const handleAction = async () => {
  // Base web implementation
  let result = await webImplementation();
  
  // Enhance with platform capabilities
  if (platformBridge?.hasFeature('native-dialog')) {
    result = await platformBridge.showNativeDialog();
  }
  
  return result;
};
```

#### **3. Shared Type Definitions**
```typescript
// packages/shared/src/types/platform.ts
export interface PlatformCapabilities {
  fileSystem: boolean;
  notifications: boolean;
  nativeDialogs: boolean;
}

export interface PlatformBridge {
  getCapabilities(): PlatformCapabilities;
  hasFeature(feature: keyof PlatformCapabilities): boolean;
}
```

### **Framework-Specific Considerations**

#### **React (Optional)**
```typescript
// apps/client/vite.config.ts
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // ... rest of config
});
```

#### **Vue**
```typescript
// apps/client/vite.config.ts
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  // ... rest of config
});
```

#### **Svelte**
```typescript
// apps/client/vite.config.ts
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  // ... rest of config
});
```

#### **Angular**
```typescript
// apps/client/vite.config.ts
import angular from '@analogjs/vite-plugin-angular';

export default defineConfig({
  plugins: [angular()],
  // ... rest of config
});
```

This framework-agnostic approach ensures your monorepo maintains the core philosophy of "single codebase, multiple deployment targets" while providing flexibility to choose the best frontend framework for your team and project requirements. 
