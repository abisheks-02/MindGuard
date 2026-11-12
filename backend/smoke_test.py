from app.main import app

print("App factory OK:", app.title)
print("Version:", app.version)
print()
print("Registered routes:")
for route in app.routes:
    if hasattr(route, "methods"):
        print(f"  {','.join(route.methods):8s} {route.path}")
    elif hasattr(route, "path"):
        print(f"  {'MOUNT':8s} {route.path}")
