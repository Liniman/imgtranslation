#!/usr/bin/env python3
"""
Diagnose network connectivity issues.
"""

import socket
import subprocess
import sys
import time

def test_port_binding(port):
    """Test if we can bind to a port."""
    try:
        # Try to create a socket and bind to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Try different addresses
        addresses = [
            ('127.0.0.1', port),
            ('localhost', port),
            ('0.0.0.0', port),
        ]
        
        for addr, p in addresses:
            try:
                print(f"Testing {addr}:{p}... ", end='')
                sock.bind((addr, p))
                sock.listen(1)
                print("✅ SUCCESS - Can bind to this address")
                sock.close()
                return True, addr
            except Exception as e:
                print(f"❌ FAILED - {str(e)}")
                continue
        
        return False, None
        
    except Exception as e:
        print(f"Socket creation failed: {e}")
        return False, None

def test_simple_server(host='127.0.0.1', port=9999):
    """Test a simple HTTP server."""
    print(f"\n🧪 Testing simple HTTP server on {host}:{port}")
    
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import threading
    
    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Suppress logs
    
    try:
        server = HTTPServer((host, port), Handler)
        
        # Run server in thread
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        
        print(f"✅ Server started on http://{host}:{port}")
        
        # Test connection
        time.sleep(1)
        import urllib.request
        try:
            response = urllib.request.urlopen(f'http://{host}:{port}', timeout=2)
            print("✅ Successfully connected to test server!")
            return True
        except Exception as e:
            print(f"❌ Could not connect to test server: {e}")
            return False
        finally:
            server.shutdown()
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def check_system_info():
    """Check system configuration."""
    print("\n📊 System Information:")
    
    # Python version
    print(f"Python: {sys.version}")
    
    # Check for common issues
    try:
        # Check if another process might be interfering
        result = subprocess.run(['lsof', '-i', ':5000'], capture_output=True, text=True)
        if result.stdout:
            print(f"⚠️  Port 5000 in use: {result.stdout}")
    except:
        pass
    
    # Check hosts file
    try:
        with open('/etc/hosts', 'r') as f:
            hosts_content = f.read()
            if '127.0.0.1' in hosts_content:
                print("✅ /etc/hosts contains 127.0.0.1")
            else:
                print("❌ /etc/hosts missing 127.0.0.1 entry")
    except:
        print("⚠️  Could not read /etc/hosts")

def main():
    print("🔍 Diagnosing Network Connectivity Issues")
    print("=" * 40)
    
    # Test different ports
    test_ports = [5000, 8501, 8502, 9999]
    working_configs = []
    
    for port in test_ports:
        print(f"\n📌 Testing port {port}:")
        success, addr = test_port_binding(port)
        if success:
            working_configs.append((addr, port))
    
    # Test simple server
    if working_configs:
        host, port = working_configs[0]
        test_simple_server(host, port)
    
    # System info
    check_system_info()
    
    # Recommendations
    print("\n💡 Recommendations:")
    if working_configs:
        print(f"✅ Use these working configurations:")
        for addr, port in working_configs:
            print(f"   - http://{addr}:{port}")
    else:
        print("❌ No ports could be bound. Possible issues:")
        print("   - Firewall blocking connections")
        print("   - Security software interference")
        print("   - System configuration issues")
        
    print("\n🔧 Try these solutions:")
    print("1. Check System Preferences > Security & Privacy > Firewall")
    print("2. Try running: sudo killall -9 python3")
    print("3. Restart your terminal/computer")
    print("4. Try using a different port (e.g., 9999)")

if __name__ == "__main__":
    main()