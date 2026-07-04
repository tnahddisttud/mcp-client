# MCP Client

This directory contains the client applications to interact with the HRMS MCP server.

## Running the UI

We have a Streamlit-based user interface for the MCP client.

To run it:
1. Make sure your MCP server (e.g., HRMS) is running on `http://localhost:8080/mcp`.
2. Install dependencies via `uv sync` or ensure your environment is set up.
3. Start the Streamlit application:
   ```bash
   uv run streamlit run app.py
   ```

## Running the Console Client

If you prefer a command-line interface, you can run the original Python script:
```bash
uv run python main.py
```
