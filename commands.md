 <!-- ```
   curl -X 'GET' \
   'http://localhost:8000/nodes/SITEID1' \
   -H 'accept: application/json'
  ``` -->
   <!-- uvicorn topology_server:app --reload -->

   <!-- Start SC + add demo functions from another window (4)

   ```
   git clone https://github.com/nubispc/desire6g-service-catalog
   cd desire6g-service-catalog
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app:app --reload --host 0.0.0.0 --port 8001
   curl -X POST -H "Content-Type: application/json" -d '{"name": "graph1", "data": {"nodes": ["A", "B"], "edges": ["A", "B"]}}' http://localhost:8001/store
   ``` -->
   <!-- uvicorn server:app --reload -->