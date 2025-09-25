from app import FlexygentApp



if __name__ == "__main__":
    # app = FlexygentApp(config_paths=['config/custom.yaml'])

    app = FlexygentApp()
    try:
        app.run()
    finally:
        app.close()  # Ensures cleanup even on exceptions
    # Or use context: with FlexygentApp() as app: app.run()