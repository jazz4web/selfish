from starlette.responses import PlainTextResponse


async def show_index(request):
    return PlainTextResponse(
        'Сайт в стадии разработки, попробуйте зайти позже.')
