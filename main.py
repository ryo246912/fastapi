from fastapi import FastAPI, Query, Path, Body,Cookie,Header,status,Form
from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Union, List

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    description: Union[str, None] = None
    tax: float = 10.5
    tags: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item2",
                "price": 35.4,
                "tax": 3.2,
                "tags":["test"],
            }
        }

class Item2(BaseModel):
    name: str
    description: str

class BaseItem(BaseModel):
    description: str
    type: str

class CarItem(BaseItem):
    type = "car"

class PlaneItem(BaseItem):
    type = "plane"
    size: int

class User(BaseModel):
    username: str
    full_name: Union[str, None] = None

    class Config:
        schema_extra = {
            "example": {
                "username": "Test",
                "full_name": "testname",
            }
        }

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Union[str, None] = None

class UserIn(UserBase):
    password: str

class UserOut(UserBase):
    pass

class UserInDB(UserBase):
    hashed_password: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str = None):
#     return {"item_id": item_id, "q": q}

# @app.get("/items/")
# async def read_item(skip: int = 0, limit: int = 10):
#     return fake_items_db[skip : skip + limit]

@app.get("/items/")
async def read_items(q: Union[List[str], None] = Query(default=None),
    r: Union[str, None] = Query(
        default=None,
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
        min_length=3,
        # deprecated=True,
    ),
    ads_id: Union[str, None] = Cookie(default=None),
    user_agent: Union[str, None] = Header(default=None)
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}],"ads_id": ads_id,"User-Agent": user_agent}
    if q:
        results.update({"q": q})
    if r:
        results.update({"r": r})
    return results

@app.post("/items/",response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item

@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(title="The ID of the item to get", ge=1),
    q: Union[str, None] = Query(default=None, alias="item-query"), 
    short: bool = False
):
    i = {"item_id": item_id,"items":items[item_id]}
    if q:
        i.update({"q": q})
    if not short:
        i.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return i

items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
    "baz2": {
        "name": "Baz2",
        "description": "There goes my baz",
        "price": 50.2,
        "tax": 10.5,
    },
}

@app.get("/items2/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: str):
    return items[item_id]

@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"}, # includeはkeyを一部に
)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"}) # excludeはkeyを除く
async def read_item_public_data(item_id: str):
    return items[item_id]

@app.put("/items/{item_id}")
def update_item(
        item_id: int, 
        item: Item = Body(
            examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        )
    ):
    return {"item_name": item.name, "item_id": item_id}

#FIXME 複数のパラメータにBodyを渡した際に、Docに効かない
@app.put("/items/{item_id2}")
def update_item2(
        item_id2: int, 
        user: User = Body(
            examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "username": "Test",
                        "full_name": "testname",
                    },
                },
            }
        ),
        item: Item = Body(
            examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        )
    ):
    return {"item_name": item.name,"user_name": user.username, "item_id": item_id2}


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password

def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(),hashed_password=hashed_password)
    print(user_in,user_in_db)
    print("User saved! ..not really")
    return user_in_db


@app.post("/user/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved


items3 = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        # "type": "plane",
        "size": 5,
    },
}

@app.get("/items3/{item_id}", response_model=Union[PlaneItem, CarItem])
async def read_item(item_id: str):
    return items3[item_id]


items2 = [
    {"name": "Foo", "description": "There comes my hero"},
    {"name": "Red", "description": "It's my aeroplane"},
]


@app.get("/items2/", response_model=List[Item2])
async def read_items():
    return items2

#MEMO DRFだとFormの受取はどう書く？
@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}