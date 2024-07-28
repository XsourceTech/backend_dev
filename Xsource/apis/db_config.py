from tortoise import Tortoise

db_config = {
    "connections": {
        "default": "mysql://root:@localhost:3306/xsource"
    },
    "apps": {
        "models": {
            "models": ["models"],
            "default_connection": "default",
        }
    }
}


async def init():
    await Tortoise.init(config=db_config)
    await Tortoise.generate_schemas()
