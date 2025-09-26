# Flexygent Client Implementation Plan

## 🎯 **Client App Specifications**

### **Headless Process Requirements**
- **No UI**: Pure background service
- **System Privileges**: Admin/root access for system operations
- **Auto-start**: Boot with system
- **Lightweight**: Minimal resource usage
- **Cross-platform**: Windows, macOS, Linux

## 🔧 **Technology Stack Recommendations**

### **Language Choice: Go (Recommended)**

**Why Go?**
- **Single Binary**: Easy deployment, no dependencies
- **Cross-platform**: Compile for Windows, macOS, Linux
- **Performance**: Fast execution, low memory usage
- **Concurrency**: Excellent for WebSocket connections
- **System Access**: Good libraries for OS operations
- **Security**: Memory safety, no buffer overflows

**Alternative: Rust**
- **Pros**: Memory safety, performance, system access
- **Cons**: Steeper learning curve, longer compile times

**Alternative: C++**
- **Pros**: Maximum performance, system access
- **Cons**: Memory management complexity, platform-specific code

### **Communication Protocol: WebSocket + JSON**

**Why WebSocket?**
- **Real-time**: Bidirectional communication
- **Low Latency**: No HTTP overhead for each message
- **Persistent**: Maintains connection state
- **Efficient**: Binary frames, compression support
- **Cross-platform**: Standard protocol

**Message Format: JSON**
```json
{
  "type": "task_request",
  "id": "task_12345",
  "client_id": "device_abc123",
  "session_token": "encrypted_token",
  "command": "file.write",
  "parameters": {
    "path": "/home/user/file.txt",
    "content": "Hello World"
  },
  "privilege_level": 2,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🏗️ **Client Architecture**

### **Core Components**
```go
type FlexygentClient struct {
    // Connection
    conn        *websocket.Conn
    serverURL   string
    clientID    string
    sessionToken string
    
    // System Access
    privilegeLevel int
    systemTools    *SystemTools
    
    // Communication
    messageQueue   chan Message
    responseQueue  chan Response
    
    // State
    isConnected    bool
    isRunning      bool
    lastHeartbeat  time.Time
}
```

### **System Tools Interface**
```go
type SystemTools struct {
    FileSystem    *FileSystemTool
    ProcessMgr    *ProcessManager
    SystemInfo    *SystemInfoTool
    NetworkMgr    *NetworkManager
    RegistryMgr   *RegistryManager  // Windows only
    ServiceMgr    *ServiceManager
}

type FileSystemTool struct {
    // File operations
    Read(path string) ([]byte, error)
    Write(path string, content []byte) error
    Delete(path string) error
    Copy(src, dst string) error
    Move(src, dst string) error
    List(dir string) ([]FileInfo, error)
    Search(pattern string) ([]string, error)
}

type ProcessManager struct {
    // Process operations
    List() ([]ProcessInfo, error)
    Start(command string) (int, error)
    Stop(pid int) error
    Monitor(pid int) (ProcessStatus, error)
}
```

## 📡 **Communication Protocol Details**

### **Connection Establishment**
```go
// 1. Client connects to server
conn, err := websocket.Dial(serverURL, "", "http://localhost")

// 2. Send authentication
authMsg := AuthMessage{
    Type: "auth",
    ClientID: clientID,
    DeviceInfo: getDeviceInfo(),
    PublicKey: publicKey,
}

// 3. Server responds with session token
response := <-responseQueue
sessionToken = response.SessionToken
```

### **Message Types**
```go
const (
    MSG_AUTH = "auth"
    MSG_TASK_REQUEST = "task_request"
    MSG_TASK_RESPONSE = "task_response"
    MSG_HEARTBEAT = "heartbeat"
    MSG_ERROR = "error"
    MSG_LOG = "log"
)
```

### **Task Execution Flow**
```go
// 1. Receive task from server
task := <-messageQueue

// 2. Validate privilege level
if task.PrivilegeLevel > client.privilegeLevel {
    return ErrorResponse("Insufficient privileges")
}

// 3. Execute command
result, err := client.systemTools.Execute(task.Command, task.Parameters)

// 4. Send response
response := TaskResponse{
    Type: MSG_TASK_RESPONSE,
    TaskID: task.ID,
    Status: "success",
    Result: result,
    Error: err,
}
client.Send(response)
```

## 🔐 **Security Implementation**

### **Authentication Flow**
```go
// 1. Generate device ID (first run)
deviceID := generateDeviceID()

// 2. Register with server
registration := RegistrationRequest{
    DeviceID: deviceID,
    DeviceInfo: getDeviceInfo(),
    PublicKey: generateKeyPair(),
}

// 3. Server responds with encrypted token
token := serverResponse.EncryptedToken

// 4. Store token securely
storeTokenSecurely(token)
```

### **Message Encryption**
```go
// Encrypt sensitive data
encryptedData, err := encrypt(data, serverPublicKey)

// Decrypt server messages
decryptedData, err := decrypt(encryptedData, clientPrivateKey)
```

### **Privilege Levels**
```go
const (
    PRIVILEGE_BASIC = 1      // Read files, list processes
    PRIVILEGE_DEVELOPMENT = 2 // Write files, start processes
    PRIVILEGE_SYSTEM = 3     // Registry, services
    PRIVILEGE_ROOT = 4       // Full system access
)
```

## 🚀 **Server Modifications Required**

### **1. Add WebSocket Support**
```python
# Add to app.py
from fastapi import FastAPI, WebSocket
import asyncio
import json

class ClientManager:
    def __init__(self):
        self.clients = {}  # client_id -> websocket
        self.task_queue = asyncio.Queue()
    
    async def register_client(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.clients[client_id] = websocket
        print(f"Client {client_id} connected")
    
    async def send_task(self, client_id: str, task: dict):
        if client_id in self.clients:
            websocket = self.clients[client_id]
            await websocket.send_text(json.dumps(task))
    
    async def handle_response(self, client_id: str, response: dict):
        # Process client response
        print(f"Response from {client_id}: {response}")

# Add WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await client_manager.register_client(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            response = json.loads(data)
            await client_manager.handle_response(client_id, response)
    except WebSocketDisconnect:
        del client_manager.clients[client_id]
```

### **2. Add Client Tools to Registry**
```python
# Add to src/tools/system/
class ClientFileTool(BaseTool):
    name = "client.file"
    description = "File operations on client device"
    
    async def execute(self, params: dict, context: dict = None):
        # Send command to client
        task = {
            "command": "file.write",
            "parameters": params,
            "client_id": context.get("client_id")
        }
        return await client_manager.send_task(task)

class ClientProcessTool(BaseTool):
    name = "client.process"
    description = "Process management on client device"
    
    async def execute(self, params: dict, context: dict = None):
        task = {
            "command": "process.start",
            "parameters": params,
            "client_id": context.get("client_id")
        }
        return await client_manager.send_task(task)
```

### **3. Modify Agent Factory**
```python
# Add client tools to agent configurations
def _create_default_agents_for_genesis(self) -> Dict[str, BaseAgent]:
    # ... existing code ...
    
    # Add client tools to each agent
    for agent_name, agent in agents.items():
        if hasattr(agent, 'tools'):
            agent.tools.extend([
                ClientFileTool(),
                ClientProcessTool(),
                ClientSystemTool(),
            ])
    
    return agents
```

## 📦 **Client Deployment**

### **Build Process**
```bash
# Cross-platform build
GOOS=windows GOARCH=amd64 go build -o flexygent-client.exe
GOOS=linux GOARCH=amd64 go build -o flexygent-client-linux
GOOS=darwin GOARCH=amd64 go build -o flexygent-client-macos
```

### **Installation Scripts**
```bash
# Windows (PowerShell)
# Install as Windows Service
sc create "FlexygentClient" binPath="C:\Program Files\Flexygent\flexygent-client.exe"
sc start "FlexygentClient"

# Linux (systemd)
# Create service file
sudo cp flexygent-client.service /etc/systemd/system/
sudo systemctl enable flexygent-client
sudo systemctl start flexygent-client

# macOS (launchd)
# Create plist file
sudo cp com.flexygent.client.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/com.flexygent.client.plist
```

## 🔄 **Development Workflow**

### **1. Client Development**
```bash
# Initialize Go module
go mod init flexygent-client

# Add dependencies
go get github.com/gorilla/websocket
go get github.com/shirou/gopsutil/v3/process
go get github.com/shirou/gopsutil/v3/system

# Run in development
go run main.go --dev --server-url ws://localhost:8000/ws
```

### **2. Server Integration**
```bash
# Add WebSocket support to FastAPI
pip install websockets

# Test connection
python -m websockets ws://localhost:8000/ws/test_client
```

### **3. Testing**
```bash
# Unit tests
go test ./...

# Integration tests
go test -tags=integration ./...

# End-to-end tests
python test_client_server.py
```

## 📊 **Performance Considerations**

### **Client Optimization**
- **Connection Pooling**: Reuse WebSocket connections
- **Message Batching**: Batch multiple commands
- **Compression**: Enable WebSocket compression
- **Heartbeat**: Keep connection alive
- **Reconnection**: Auto-reconnect on failure

### **Server Optimization**
- **Async Processing**: Handle multiple clients concurrently
- **Task Queue**: Queue tasks for busy clients
- **Load Balancing**: Distribute load across servers
- **Caching**: Cache frequent operations
- **Rate Limiting**: Prevent client overload

## 🚨 **Security Best Practices**

### **Client Security**
- **Code Signing**: Sign executables
- **Integrity Checks**: Verify client integrity
- **Sandboxing**: Run in restricted environment
- **Audit Logging**: Log all operations
- **Update Mechanism**: Secure update process

### **Server Security**
- **Authentication**: Strong client authentication
- **Authorization**: Role-based access control
- **Encryption**: End-to-end encryption
- **Rate Limiting**: Prevent abuse
- **Monitoring**: Real-time security monitoring

This implementation provides a robust, secure, and efficient client-server architecture for Flexygent with headless client operation and full system access capabilities.
