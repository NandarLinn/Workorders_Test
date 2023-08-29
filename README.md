# Chat With Dabase Using LangChain

### Install the dependencies
- Create a new virtual environment
```sh
python3 -m venv workorders_env
source testwork_env/bin/activate
```
- install required library using pip
```sh
pip install -r requirement.txt
```

### Create SqliteDB
To execute the API, please use the following command:
```sh
uvicorn app:app --reload
```
- Upon executing the API, the database and corresponding tables were automatically created in `database/sql_app.db`. It is worth noting that an SQLite Database was utilized for this demonstration application.
- First of all, the denormalized dataset needs to be normalized that helps eliminate data redundancy and improve data integrity in the database. It involves organizing data into tables and applying a set of rules called normal forms to ensure efficient and accurate data storage. After the process of normalization, a total of four tables are obtained.
    - MaidRequests
    - CleaningRequests
    - TechnicianRequests
    - AminetyRequests
    - Rooms
    - Staffs
    - Guests
- To review the table schema, kindly refer to the [Model](https://github.com/NandarLinn/Workorders/tree/main/app/models) folder.
 
### Importing CSV Data
The first step involves mapping the CSV header to the respective column mapping. Following this, the sale data is read row by row, and the data is imported into specific tables using filter methods.
Dataset is created manually based on the own model
To import the CSV data, please execute the following command:
```
python -m seeds.importer_rooms_and_staffs <rooms_and_staffs_.csv path)
```
```sh
python -m seeds.importer_guests <guest.csv path>
```

### Building A Chat Bot for recommendation
The current database is connected to Langchain, a tool known as large language models (LLMs), that helps connect advanced language software, with other sources of information, like databases. But there has limitation for free api key.
```sh
def convert_prompt_to_query(prompt):
    llm = OpenAI(temperature=0, openai_api_key='OPEN_API_KEY')
    db_uri = DB_URI
    db = SQLDatabase.from_uri(db_uri)
    db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)

    result = db_chain.run(prompt)
    return result
```
Please refer to the code in the [recommender.py](https://github.com/NandarLinn/Workorders/blob/main/app/apis/v1/recommender.py) and [prompt_to_query.py](https://github.com/NandarLinn/Workorders/blob/main/app/modules/prompt_to_query.py) file for further details and implementation.

### Run Demo App
To execute the API, please use the following command:
```sh
uvicorn app:app --reload
```
Through the Fast API, it is possible to inquire about create and updated for coming requests. A Bot is also add for recommendation. But need to improve performance and effenciency.
Try it out in browser
```sh
http://127.0.0.1:8000/docs
```
![Alt](https://github.com/NandarLinn/Workorders/blob/main/pictures/1.png)
