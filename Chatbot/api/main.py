from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import Chatbot.api.generic_helper as generic_helper
import logging

# Set up FastAPI app
app = FastAPI()

# Initialize in-progress orders storage
inprogress_orders = {}

# Set up logging for tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()
    logging.info(f"Received payload: {payload}")

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])

    # Map intents to functions
    intent_handler_dict = {
        'order.add - context: ongoing-order': add_to_order,
        'order.remove - context: ongoing-order': remove_from_order,
        'order.complete - context: ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order
    }

    # Call the appropriate function
    if intent in intent_handler_dict:
        return await intent_handler_dict[intent](parameters, session_id)
    else:
        logging.warning(f"Intent '{intent}' not recognized.")
        return JSONResponse(content={"fulfillmentText": "Intent not recognized. Please try again."})


async def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding your order. Can you please place a new order?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error. Please try again."
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Order placed successfully! Your order id is #{order_id}. Total: {order_total}."

        # Clear the order session
        del inprogress_orders[session_id]

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


async def add_to_order(parameters: dict, session_id: str):
    tech_items = parameters.get("tech-item", [])
    quantities = parameters.get("number", [])

    if len(tech_items) != len(quantities):
        return JSONResponse(content={"fulfillmentText": "Please specify both tech items and quantities."})

    # Update session order with new items and quantities
    new_tech_dict = dict(zip(tech_items, quantities))
    if session_id in inprogress_orders:
        inprogress_orders[session_id].update(new_tech_dict)
    else:
        inprogress_orders[session_id] = new_tech_dict

    # Prepare response string
    order_str = generic_helper.get_str_from_tech_dict(inprogress_orders[session_id])
    fulfillment_text = f"Currently, you have: {order_str}. Anything else?"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


async def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return JSONResponse(content={"fulfillmentText": "No active order found. Can you please place a new order?"})

    tech_items = parameters.get("tech-item", [])
    current_order = inprogress_orders[session_id]
    removed_items, no_such_items = [], []

    for item in tech_items:
        if item in current_order:
            removed_items.append(item)
            del current_order[item]
        else:
            no_such_items.append(item)

    fulfillment_text = ""
    if removed_items:
        fulfillment_text += f"Removed {', '.join(removed_items)} from your order!"
    if no_such_items:
        fulfillment_text += f" No such items found: {', '.join(no_such_items)}."

    if not current_order:
        fulfillment_text += " Your order is now empty!"
    else:
        order_str = generic_helper.get_str_from_tech_dict(current_order)
        fulfillment_text += f" Remaining items: {order_str}"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


async def track_order(parameters: dict, session_id: str):
    try:
        order_id = int(parameters['number'])
    except ValueError:
        return JSONResponse(content={"fulfillmentText": "Invalid order ID. Please provide a valid number."})

    order_status = db_helper.get_order_status(order_id)
    if order_status:
        fulfillment_text = f"Order status for #{order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with ID #{order_id}"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()

    for tech_item, quantity in order.items():
        price = db_helper.get_item_price(tech_item)
        ids = db_helper.get_item_id(tech_item)
        if price is None:
            logging.error(f"Tech item '{tech_item}' not found in database.")
            return -1

        if db_helper.insert_order(next_order_id, ids, quantity, price,tech_item) == -1:
            logging.error(f"Failed to insert item '{tech_item}' into orders.")
            return -1

    # Add tracking info
    db_helper.insert_order_tracking(next_order_id, "in progress")
    return next_order_id


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="127.0.0.1", port=8000)
