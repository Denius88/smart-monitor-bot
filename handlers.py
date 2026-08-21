from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.future import select

from database import AsyncSessionLocal
from models import User, TrackedItem
from scraper import check_price

router = Router()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Add Item"),
            KeyboardButton(text="📋 My Items")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Choose an action below..."
)

class AddItem(StatesGroup):
    waiting_for_url = State()
    waiting_for_price = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Welcome to Smart Monitor Bot!\n\n"
        "Use the buttons below to manage your tracking list.",
        reply_markup=main_kb
    )

@router.message(Command("add"))
@router.message(F.text == "➕ Add Item")
async def cmd_add(message: Message, state: FSMContext):
    await message.answer("🔗 Please send me the URL of the product you want to track:")
    await state.set_state(AddItem.waiting_for_url)

@router.message(AddItem.waiting_for_url)
async def process_url(message: Message, state: FSMContext):
    if not message.text.startswith("http"):
        await message.answer("❌ This doesn't look like a valid link. Please send a URL starting with http:// or https://")
        return
        
    await state.update_data(url=message.text)
    await message.answer("💰 What is your target price? (Enter a number, e.g., 500)")
    await state.set_state(AddItem.waiting_for_price)

@router.message(AddItem.waiting_for_price)
async def process_price(message: Message, state: FSMContext):
    """Receive target price and save to database."""
    try:
        target_price = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("❌ Invalid format. Please enter a number (e.g., 500).")
        return

    data = await state.get_data()
    url = data['url']
    user_id = message.from_user.id
    username = message.from_user.username

    await message.answer("⏳ Checking the current price... Please wait.")
    
    current_price = await check_price(url)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(id=user_id, username=username)
            session.add(user)

        new_item = TrackedItem(
            user_id=user_id,
            url=url,
            current_price=current_price,
            target_price=target_price
        )
        session.add(new_item)
        await session.commit()

    price_msg = f"Current price: {current_price}" if current_price else "Could not fetch current price, but will keep tracking."
    await message.answer(f"✅ Item saved successfully!\n\n{price_msg}\nTarget Price: {target_price}")
    await state.clear()

@router.message(Command("list"))
@router.message(F.text == "📋 My Items")
async def cmd_list(message: Message):
    """Show all tracked items for the user."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(TrackedItem).where(TrackedItem.user_id == message.from_user.id)
        )
        items = result.scalars().all()

    if not items:
        await message.answer("📭 Your tracking list is empty. Click '➕ Add Item' to start.")
        return

    text = "📋 **Your Tracked Items:**\n\n"
    for item in items:
        curr = item.current_price if item.current_price else "Unknown"
        text += f"🔗 URL: {item.url}\n💵 Current: {curr} | 🎯 Target: {item.target_price}\n\n"

    await message.answer(text, disable_web_page_preview=True)