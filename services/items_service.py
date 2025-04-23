import logging
from urllib.request import Request

from fastapi import HTTPException
from models.item_model import Item
from datetime import datetime

def create_item(new_item, repository) -> str:
    try:
        new_uuid = repository.create_item(new_item)
        if not isinstance(new_uuid, str):
            raise TypeError("The method create_item did not return a str.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the item: {e}")

    return new_uuid

def get_items(filters, repository) -> list[Item]:
    logging.info("Getting all items")
    #try:
    items = repository.list_items(filters)
    logging.info(f"Found {len(items)} items")
    logging.info(items)
    try:
        if not isinstance(items, list):
            raise TypeError("The method list_items did not return a list.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while get the list of items: {e}")

    return items


def get_item(uuid: str, repository) -> Item:
    try:
        item = repository.get_item(uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while get item: {e}")

    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return item

def update_item(uuid: str, item_update: Item, repository) -> None:
    try:
        repository.update_item(uuid, item_update)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while updating the item: {e}")

def delete_item(uuid: str, repository) -> None:
    try:
        repository.delete_item(uuid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while deleting the item: {e}")
