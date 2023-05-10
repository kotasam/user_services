# Base Template for Micro Service

#### Commands to use:

* "make env-setup" - This commands helps use to remove any existing virtual environments and create a new one with the 
  requirements specified from the requirements.txt.

* "make run-{env}" - where env can be any of local, dev or prod. This command sources the respective config file and 
  pulls the settings from that respective config. It will make necessary migrations and run the server accordingly. 
  <br>
__Note__: Production server is triggered using gunicorn rather than starting a simple server.

* To create proto files run the below command
  ```
  python -m grpc_tools.protoc -I common/grpc/protobufs --python_out=common/grpc/protopys --grpc_python_out=common/grpc/protopys common/grpc/protobufs/*
  ```

* "make run-grpc-{env}" - this command is used to Run grpc server

#### File Structure:

All the required setup files will reside in common file only like middlewares, grpc, swagger, configs, database 
```
    .
    ├── src/                                # the root or main folder of django
    │   └── *                               # all the default files
    ├── common/                             # stores all third party setups and there configurations
    │   ├── configs/                        # will contain configuration files
    │   │   ├── users/                      # any user specific configuration will be stored here   
    │   │   └── *.cfg                       # general configuration files like local and dev will here
    │   │
    │   ├── database/                       # database related configuration stored here
    │   │   └── db_routers.py               # helpful in changing default migration schema
    │   │
    │   ├── events/                         # it contains any function related to async task
    │   │   ├── consumers/                  # all consumers files must be placed in this
    │   │   │    └── *_consumer.py          # these files are used to for listening any published events
    │   │   │
    │   │   └── publishers                  # all publishers files must be placed in this
    │   │       └── *_publisher.py          # these files are used to for publisher events which are consumed by others
    │   │
    │   ├── grpc/                           # will contain grpc files
    │   │   ├── actions/                    # grpc function which get information from other servers
    │   │   │   └── *_action.py             # these functions fetch information
    │   │   │   
    │   │   ├── protobugs/                  # it contain proto files
    │   │   │    └── *.proto                # these files are used to generate enum kind functions and varaibles
    │   │   │
    │   │   ├── protopys/                   # containes proto file generated functions
    │   │   │   ├──  *_pb2_grpc.py          # proto generated function resides in this function
    │   │   │   └──  *_pb2.py               # proto generated varaible reside in this
    │   │   │
    │   │   └── services/                   # grpc function which send information to other servers
    │   │       └──  *_service.py           # these functions will be called by outside server for information
    │   │ 
    │   ├── middlewares/                    # will contain middlewares files
    │   │    └── *_middleware.py            # custom middlewares for performing actions one such example is jwt_middleware
    │   │
    │   ├── swagger/                        # will contain swagger configuration
    │   │   └──  documentaion.py            # all kind of swagger documents will reside in this file
    │   │
    │   └── logs/                           # will contain logs configuration
    │       └──  logger.py                  # new relic log configuration has been added here
    │   
    ├── manage.py                           # default djano file to run dev server
    ├── grpc_server.py                      # grpc server function to run a gRPC server
    └── requirements.txt                    # it contains all the required libraries
```