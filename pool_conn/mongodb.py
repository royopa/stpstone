import pandas as pd
from pymongo import MongoClient
from logging import Logger
from typing import Optional
from __future__ import annotations
from stpstone.loggs.create_logs import CreateLog


class MongoConn:

    _instance: MongoConn | None = None

    def __new__(cls:type[MongoConn], *args, **kwargs) -> MongoConn:
        '''
        DOCSTRING: ENSURES THAT ONLY ONE INSTANCE OF THE CLASS IS CREATED (SINGLETON PATTERN)
        INPUTS: ARGS, KWARGS
        OUTPUS: MONGOCONN INSTANCE
        '''
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
            cls._instance.db = None
            cls._instance._collection = None
        return cls._instance

    def __init__(self, str_host:str='localhost', int_port:int=27017, str_dbname:str='test', str_collection:str='data', 
                 logger:Optional[Logger]=None) -> None:
        '''
        DOCSTRING: INITIALIZES THE CONNECTION TO MONGODB
        INPUTS:
            str_host (str): ADDRESS OF THE MONGODB SERVER
            int_port (int): PORT OF THE MONGODB SERVER
            str_dbname (str): NAME OF THE DATABASE
            str_collection (str): NAME OF THE COLLECTION
            logger (Optional[Logger]): LOGGER INSTANCE FOR LOGGING
        OUTPUTS: -
        '''
        if self._client is None:
            self.str_host = str_host
            self.int_port = int_port
            self.str_dbname = str_dbname
            self.str_collection = str_collection
            self.logger = logger
            self._connect

    @property
    def _connect(self) -> None:
        '''
        DOCSRTING: CONNECTS TO THE MONGODB SERVER AND INITIALIZES THE DATABASE AND COLLECTION
        INPUTS: -
        OUTPUTS: -
        '''
        self._client = MongoClient(self.str_host, self.int_port)
        self._db = self._client[self.str_dbname]
        self._collection = self._db[self.str_collection]

    def save_df(self, df_:pd.DataFrame) -> None:
        '''
        DOCSTRING: SAVES A PANDAS DATAFRAME TO THE MONGODB COLLECTION
        INPUTS:
            df_ (pd.DataFrame): DATAFRAME TO BE SAVED
        OUTPUTS: -
        '''
        if not isinstance(df_, pd.DataFrame):
            raise ValueError("THE PROVIDED DATA IS NOT A PANDAS DATAFRAME.")
        data = df_.to_dict(orient='records')
        try:
            self._collection.insert_many(data)
        except Exception as e:
            if self.logger is not None:
                CreateLog().infos(self.logger, f'ERROR {e}, MONGODB INJECTION ABORTED')

    @property
    def close(self) -> None:
        '''
        DOCSTRING: CLOSES THE CONNECTION TO THE MONGODB SERVER
        INPUTS: -
        OUTPUTS: -
        '''
        if self._client:
            self._client.close()

    def __enter__(self) -> MongoConn:
        '''
        DOCSTRING: RETURNS THE INSTANCE FOR USE IN A CONTEXT MANAGER
        INPUTS: -
        OUTPUTS: MONGOCONN INSTANCE
        '''
        return self

    def __exit__(self, exc_type: Optional[type[BaseException]], exc_val: Optional[BaseException], 
                 exc_tb: Optional[BaseException]) -> None:
        '''
        DOCSTRING: CLOSES THE CONNECTION WHEN EXITING THE CONTEXT
        INPUTS:
            exc_type: EXCEPTION TYPE
            exc_val: EXCEPTION VALUE
            exc_tb: TRACEBACK
        OUTPUTS: -
        '''
        self.close