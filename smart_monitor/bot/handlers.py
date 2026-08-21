from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.future import select

from ..database import AsyncSessionLocal
from ..models import PriceHistory, User, TrackedItem
from ..services.scraper import check_price

router = Router()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Add Item"), KeyboardButton(text="📋 My Items")],
        [KeyboardButton(text="📈 Price History"), KeyboardButton(text="🗑 Delete Item")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Choose an action below..."
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Cancel")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Enter data or cancel..."
)

class AddItem(StatesGroup):
    waiting_for_url = State()
    waiting_for_price = State()
    waiting_for_interval = State()

class DeleteItem(StatesGroup):
    waiting_for_id = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear() 
    await message.answer(
        "👋 Welcome to Smart Monitor Bot!\n\n"
        "I will track prices for you and notify you when they drop.\n"
        "Use the buttons below to manage your list.",
        reply_markup=main_kb
    )

@router.message(Command("cancel"), StateFilter("*"))
@router.message(F.text == "❌ Cancel", StateFilter("*"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("There is nothing to cancel.", reply_markup=main_kb)
        return
        
    await state.clear()
    await message.answer("🚫 Action cancelled. Returning to main menu.", reply_markup=main_kb)

@router.message(Command("add"))
@router.message(F.text == "➕ Add Item")
async def cmd_add(message: Message, state: FSMContext):
    await message.answer("🔗 Please send me the URL of the product you want to track:", reply_markup=cancel_kb)
    await state.set_state(AddItem.waiting_for_url)

@router.message(AddItem.waiting_for_url)
async def process_url(message: Message, state: FSMContext):
    message_text = message.text or ""
    if not message_text.startswith(("http://", "https://")):
        await message.answer("❌ Invalid link. Please send a valid URL (http/https).", reply_markup=cancel_kb)
        return
    await state.update_data(url=message_text)
    await message.answer("💰 What is your target price? (e.g., 500 or 1500.50)", reply_markup=cancel_kb)
    await state.set_state(AddItem.waiting_for_price)

@router.message(AddItem.waiting_for_price)
async def process_price(message: Message, state: FSMContext):
    message_text = message.text or ""
    try:
        target_price = float(message_text.replace(',', '.'))
    except ValueError:
        await message.answer("❌ Invalid format. Please enter a number.", reply_markup=cancel_kb)
        return
    await state.update_data(target_price=target_price)
    await message.answer("⏱ How often should I check the price? (Enter minutes, e.g., 15, 60, 1440)", reply_markup=cancel_kb)
    await state.set_state(AddItem.waiting_for_interval)

@router.message(AddItem.waiting_for_interval)
async def process_interval(message: Message, state: FSMContext):
    message_text = message.text or ""
    if not message_text.isdigit() or int(message_text) < 1:
        await message.answer("❌ Please enter a valid number of minutes (e.g., 15).", reply_markup=cancel_kb)
        return

    interval = int(message_text)
    data = await state.get_data()
    
    await message.answer("⏳ Checking the current price... Please wait.")
    current_price = await check_price(data['url'])

    async with AsyncSessionLocal() as session:
        user_id = message.from_user.id
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(id=user_id, username=message.from_user.username)
            session.add(user)

        new_item = TrackedItem(
            user_id=user_id,
            url=data['url'],
            current_price=current_price,
            target_price=data['target_price'],
            check_interval=interval
        )
        session.add(new_item)
        await session.flush()
        if current_price is not None:
            session.add(PriceHistory(tracked_item_id=new_item.id, price=current_price))
        await session.commit()

    price_msg = f"💵 Current price: {current_price}" if current_price else "Could not fetch current price right now."
    
    await state.clear()
    await message.answer(
        f"✅ Item saved successfully!\n\n"
        f"{price_msg}\n"
        f"🎯 Target Price: {data['target_price']}\n"
        f"⏱ Checking every {interval} minutes.",
        disable_web_page_preview=True,
        reply_markup=main_kb
    )

@router.message(Command("list"))
@router.message(F.text == "📋 My Items")
async def cmd_list(message: Message, state: FSMContext):
    await state.clear() 
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(TrackedItem).where(TrackedItem.user_id == message.from_user.id))
        items = result.scalars().all()

    if not items:
        await message.answer("📭 Your tracking list is empty. Click '➕ Add Item' to start.", reply_markup=main_kb)
        return

    text = "📋 **Your Tracked Items:**\n\n"
    for item in items:
        curr = item.current_price if item.current_price else "Unknown"
        text += f"🆔 ID: {item.id}\n🔗 URL: {item.url}\n💵 Current: {curr} | 🎯 Target: {item.target_price}\n⏱ Checks every: {item.check_interval} mins\n\n"

    await message.answer(text, disable_web_page_preview=True, reply_markup=main_kb)

@router.message(Command("history"))
@router.message(F.text == "📈 Price History")
async def cmd_history(message: Message, state: FSMContext):
    await state.clear()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(TrackedItem).where(TrackedItem.user_id == message.from_user.id)
        )
        items = result.scalars().all()

        if not items:
            await message.answer("📭 Your tracking list is empty.", reply_markup=main_kb)
            return

        text = "📈 <b>Recent Price History</b>\n\n"
        for item in items:
            history_result = await session.execute(
                select(PriceHistory)
                .where(PriceHistory.tracked_item_id == item.id)
                .order_by(PriceHistory.checked_at.desc())
                .limit(5)
            )
            history = history_result.scalars().all()
            text += f"🆔 <b>Item {item.id}</b>\n🔗 {item.url}\n"
            if history:
                text += "\n".join(
                    f"💵 {entry.price:.2f} — {entry.checked_at:%Y-%m-%d %H:%M} UTC"
                    for entry in history
                )
            else:
                text += "No recorded prices yet."
            text += "\n\n"

    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=main_kb)

@router.message(Command("delete"))
@router.message(F.text == "🗑 Delete Item")
async def cmd_delete(message: Message, state: FSMContext):
    await message.answer("🗑 Please send me the **ID** of the item you want to delete:", reply_markup=cancel_kb)
    await state.set_state(DeleteItem.waiting_for_id)

@router.message(DeleteItem.waiting_for_id)
async def process_delete(message: Message, state: FSMContext):
    message_text = message.text or ""
    if not message_text.isdigit():
        await message.answer("❌ Invalid ID. Please send a number.", reply_markup=cancel_kb)
        return
    
    item_id = int(message_text)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(TrackedItem).where(
                TrackedItem.id == item_id, 
                TrackedItem.user_id == message.from_user.id
            )
        )
        item = result.scalar_one_or_none()
        
        if item:
            await session.delete(item)
            await session.commit()
            await message.answer(f"✅ Item with ID {item_id} has been deleted.", reply_markup=main_kb)
        else:
            await message.answer("❌ Item not found or it doesn't belong to you.", reply_markup=main_kb)
            
    await state.clear()