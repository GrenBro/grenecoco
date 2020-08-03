import discord
from discord.ext import commands, tasks
from itertools import cycle
from discord.utils import get
import discord.ext.commands
import urllib.parse, urllib.request, re
from discord.ext import commands, tasks
import sqlite3
from discord.utils import get
import random
import asyncio
import os
import config

client = commands.Bot(command_prefix= '.') 
client.remove_command( 'help' ) 


@client.event
async def on_ready():
	change_status.start()
	connection.commit()
	print('Bot online')
	print(client.user.id)
	print('▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬')


connection = sqlite3.connect('server.db')
cursor = connection.cursor()
connection.commit()


@client.event
async def on_ready():
	cursor.execute("""CREATE TABLE IF NOT EXISTS users (
		name TEXT,
		id INT,
		cash BIGINT,
		rep INT,
		lvl INT
		)""")

	cursor.execute("""CREATE TABLE IF NOT EXISTS shopbus(
		role_id INT,
		id INT,
		cost BIGINT
		)""")


	
for guild in client.guilds:
	for member in guild.members:
		if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
			cursor.execute(f"INSERT INTO users VALUES {member}, {member.id}, 0, 0, 1)")
			connection.commit()
		else:
			pass


	connection.commit()
	print('Bot connected')

@client.event
async def on_member_join(member):
	if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
		cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1)")
		connection.commit()
	else:
		pass


@client.command(aliases = ['add-shop'])
@commands.has_permissions( administrator = True )
async def __add_shop(ctx, role: discord.Role = None, cost: int = None):
	if role is None:
		await ctx.send(f"**{ctx.author}**, укажите роль, которую хотите добавить!")
	else:
		if cost is None:
			await ctx.send(f"**{ctx.author}**, укажите стоимость роли!")
		elif cost < 0:
			await ctx.send(f"**{ctx.author}**, укажите стоимость выше!")
		else:
			cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
			connection.commit()
			emb = discord.Embed(title = 'Успешно', description = 'Роль была успешно добавлена в магазин!:white_check_mark:', colour = discord.Color.green())
			await ctx.send(embed=emb)


@client.command(aliases = ['remove-shop'])
@commands.has_permissions( administrator = True )
async def __remove_shop(ctx, role: discord.Role = None):
	if role is None:
		await ctx.send(f"**{ctx.author}**, укажите роль, которую хотите удалить")
	else:
		cursor.execute("DELETE FROM shop WHERE role_id = {}".format(role.id))
		connection.commit()
		emb = discord.Embed(title = 'Успешно', description = 'Роль была успешно Удалена с магазина!:white_check_mark:', colour = discord.Color.red())
		await ctx.send(embed=emb)


@client.command(aliases = ['shop'])
async def __shop(ctx):
	embed = discord.Embed(title = 'Магаз')

	for row in cursor.execute("SELECT role_id, cost FROM shop WHERE id = {}".format(ctx.guild.id)):
		if ctx.guild.get_role(row[0]) != None:
			embed.add_field(
				name = f"Стоимость {row[1]}",
				value = f"Роль {ctx.guild.get_role(row[0]).mention}",
				inline = False 
			)
		else:
						pass

	await ctx.send(embed = embed)



@client.command(aliases = ['buy', 'buy role'])
async def __buy(ctx, role: discord.Role = None):
	if role is None:
		await ctx.send(f"**{ctx.author}**, укажите роль")
	else:
		if role in ctx.author.roles:
			await ctx.send(f"**{ctx.author}**, у вас эта роль уже имеется")
		elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
			await ctx.send(f"**{ctx.author}, у вас недостаточно средств**")
		else:
			await ctx.author.add_roles(role)
			cursor.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))
			connection.commit()

@client.command()
async def report(ctx, member:discord.Member=None, *, arg=None):
	message = ctx.message
	channel = client.get_channel(473885901626540032)    
	if member == None:
		await ctx.send(embed=discord.Embed(description='Укажите пользователя!', color=discord.Color.red()))
	elif arg == None:
		await ctx.send(embed=discord.Embed(description='Укажите причину жалобы!', color=discord.Color.red()))
	else:
		emb = discord.Embed(title=f'Жалоба на пользователя {member}', color=discord.Color.blue())
		emb.add_field(name='Автор жалобы:', value=f'*{ctx.author}*')
		emb.add_field(name='Причина:', value='*' +arg + '*')
		emb.add_field(name='ID жалобы:', value=f'{message.id}')
		await channel.send(embed=emb)
		await ctx.author.send('✅ Ваша жалоба успешно отправлена!')

@client.command(aliases = ['balance', '$', 'bal'])
async def __balance(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(embed = discord.Embed(
			description = f"""Баланс пользователя **{ctx.author}** состовляет **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} 💰**"""
		))
	else:
		await ctx.send(embed = discord.Embed(
		description = f"""Баланс пользователя **{member}** состовляет **{cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]} 💰**"""
	))
	connection.commit()

@client.command()
async def run(ctx, member: discord.Member = None, amount: int = 3000):
	emb = discord.Embed(title = '**Гонка!!**', description = f'Пользователь: {ctx.author.name}, бросил вызов в гонке пользователю: {member.mention}! Гонка началась! Ожидайте 5 секунд', colour = discord.Color.red())
	await ctx.send(embed = emb)
	await asyncio.sleep(5)
	a = random.randint(1, 2)
	embb = discord.Embed(title =  'Итоги!', description = f'**В соревнование:** {ctx.author.mention} и {member.mention}!\n **Побеждает:** {ctx.author.mention}!!\n **Поздравим!**\n **Его счёт пополнен на 1000**💰', colour = discord.Color.blue())
	embbb = discord.Embed(title =  'Итоги!', description = f'**В соревнование:** {ctx.author.mention} и {member.mention}!\n **Побеждает:** {member.mention}!!\n **Поздравим!**\n **Его счёт пополнен на 1000**💰**', colour = discord.Color.red())
	if a == 1:
		await ctx.send(embed = embb)
		cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
		connection.commit()
	else:
		await ctx.send(embed = embbb)
		cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
		connection.commit()

@client.command()
async def kiss(ctx, member: discord.Member):
	emb = discord.Embed(title = '💋Поцелуй!💋', description = f'**Пользователь: ``{ctx.author.name}``, поцеловал { member.mention }!💋**', colour = discord.Color.red())
	emb.set_thumbnail(url = 'https://d.radikal.ru/d43/2006/76/fb8f09103a8f.gif')
	await ctx.send( embed = emb )

@client.command()
async def hug(ctx, member: discord.Member):
	emb = discord.Embed(title = '**Объятия!**', description = f'**Пользователь: {ctx.author.name}, обнял: {member.mention}!**', colour = discord.Color.blue())

	await ctx.send(embed = emb)

@client.command()
async def mute(ctx, member: discord.Member, duration: int, *, arg):
	emb = discord.Embed(title='MUTE')
	role = discord.utils.get(ctx.guild.roles, name='Muted')
	emb.add_field(name="Замутил:",
				  value=f'{ctx.author.mention} __**замутил**__: {member.mention} __**на {duration} секунд.**__')
	emb.add_field(name="Причина:", value=f'__*{arg}*__')
	await ctx.send(embed=emb)
	await member.add_roles(role)
	await asyncio.sleep(duration)
	embed = discord.Embed(description=f'Товарищ {member.mention} успешно прошёл курс оздаровления от мута).',
						  color=discord.Colour.green())
	await ctx.send(embed=embed)
	await member.remove_roles(role)

@client.command(pass_context=True)
async def profile(ctx):
	roles = ctx.author.roles
	role_list = ""
	for role in roles:
		role_list += f"<@&{role.id}> "
	emb = discord.Embed(title='Profile', colour = discord.Colour.purple())
	emb.set_thumbnail(url=ctx.author.avatar_url)
	emb.add_field(name='Никнэйм', value=ctx.author.mention)
	emb.add_field(name="Активность", value=ctx.author.activity)
	emb.add_field(name='Роли', value=role_list)
	emb.add_field(name='Присоеденился к серверу', value=ctx.author.joined_at.strftime('%Y.%m.%d \n %H:%M:%S'))
	emb.add_field(name='Присоеденился к Discord', value=ctx.author.created_at.strftime("%Y.%m.%d %H:%M:%S"))
	if 'online' in ctx.author.desktop_status:
		emb.add_field(name="Устройство", value=":computer:Компьютер:computer:")
	elif 'online' in ctx.author.mobile_status:
		emb.add_field(name="Устройство", value=":iphone:Телефон:iphone:")
	elif 'online' in ctx.author.web_status:
		emb.add_field(name="Устройство", value=":globe_with_meridians:Браузер:globe_with_meridians:")
	emb.add_field(name="Статус", value=ctx.author.status)
	emb.add_field(name='Id', value=ctx.author.id)
	await ctx.channel.purge(limit=1)
	await ctx.send(embed = emb )

@client.command(aliases = ["user"])
async def __user(ctx, member: discord.Member = None):
	roles = member.roles
	role_list = ""
	for role in roles:
		role_list += f"<@&{role.id}> "
		emb = discord.Embed(title='Profile', colour = discord.Colour.purple())
		emb.set_thumbnail(url=member.avatar_url)
		emb.add_field(name='Никнэйм', value=member.mention)
		emb.add_field(name="Активность", value=member.activity)
		emb.add_field(name='Роли', value=role_list)
		emb.add_field(name='Присоеденился к серверу', value=member.joined_at.strftime('%Y.%m.%d \n %H:%M:%S'))
		emb.add_field(name='Присоеденился к Discord', value=member.created_at.strftime("%Y.%m.%d %H:%M:%S"))
		if 'online' in member.desktop_status:
			emb.add_field(name="Устройство", value=":computer:Компьютер:computer:")
		elif 'online' in member.mobile_status:
			emb.add_field(name="Устройство", value=":iphone:Телефон:iphone:")
		elif 'online' in member.web_status:
			emb.add_field(name="Устройство", value=":globe_with_meridians:Браузер:globe_with_meridians:")
		emb.add_field(name="Статус", value=member.status)
		emb.add_field(name='Id', value=member.id)
		await ctx.channel.purge(limit=1)
		await ctx.send(embed = emb )

@client.command(aliases = ['work'])
@commands.cooldown(1, 600, commands.BucketType.user)
async def __work(ctx):
	for row in cursor.execute(f"SELECT cash FROM users WHERE id={ctx.author.id}"):
	  LVL = row[0]
	  amount = random.randint(500, 5000)
	  await ctx.send(embed=discord.Embed(description=f'Ты заработал {amount} на работе! 💳 (команда будет доступна через 10 мин.)'))

	LVL += amount

	cursor.execute(f"UPDATE users SET cash = {LVL} WHERE id={ctx.author.id}")
	connection.commit()

@client.command()
@commands.has_permissions( administrator = True )
async def temp_ban(ctx, user : discord.Member, arg):
	await user.ban(reason=None)
	emb = discord.Embed( title = f'{user}', description = f'**Забанен на {arg} секунд:** {user}\n**Кем:** {ctx.author.name}' )
	emb.set_thumbnail( url = f'{ctx.guild.icon_url}' )
	await ctx.send(embed=emb)

	await asyncio.sleep(int(arg))

	banned_users = await ctx.guild.bans()#Получаю список забаненых
	author = ctx.message.author.mention
	for ban_entry in banned_users: 
		user = ban_entry.user #Тут мы получаем имя пользевателя без @ и теперь оно выгледет name#1234
	await ctx.guild.unban(user)

	@client.command()
	@commands.has_permissions( administrator = True )
	async def unban( self, ctx, *, member: discord.User):
		client = self.client

		banned_users = await ctx.guild.bans()

		for ban_entry in banned_users:
			user = ban_entry.user

			if ( user.name, user.discriminator ) == ( member.name, member.discriminator ):
				await ctx.guild.unban( user )

				emb = discord.Embed( description = f'**{ctx.message.author.mention} Разбанил {member.mention}**' , colour = discord.Color.green() )
				emb.set_author( name = ctx.author.name, icon_url = ctx.author.avatar_url )
				emb.set_footer( text = Footer, icon_url = client.user.avatar_url )
				
				await ctx.send( embed = emb )

				emb = discord.Embed( description = f'**Вы были разбанены на сервере {ctx.guild.name}**', colour = discord.Color.green() )

				emb.set_author( name = ctx.author.name, icon_url = ctx.author.avatar_url )
				emb.set_footer( text = Footer, icon_url = client.user.avatar_url )

				await member.send( embed = emb )
				
				return


@client.command(aliases = ['add'])
@commands.has_permissions( administrator = True )
async def __add(ctx, member: discord.Member = None, amout: int = None):
	if member is None:
		await ctx.send(f"**{ctx.author}**, укажите пользователя")
	else:
		if amout is None:
			await ctx.send(f"**{ctx.author}**, укажите сумму!")
		elif amout < 1:
			await ctx.send(f"**{ctx.author}**, Укажи сумму больше 1")
		else:
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amout, member.id))
			connection.commit()


@client.command(aliases = ['und'])
@commands.has_permissions( administrator = True )
async def __und(ctx, member: discord.Member = None, amount = None):
	if member is None:
		await ctx.send(f"**{ctx.author}**, укажите пользователя")
	else:
		if amount is None:
			await ctx.send(f"**{ctx.author}**, укажите сумму!")
		elif amount > 1:
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(0, member.id))
			connection.commit()

		elif amout < 1:
			await ctx.send(f"**{ctx.author}**, Укажи сумму больше 1")
		else:
			cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), member.id))
			connection.commit()

@client.command()
@commands.has_permissions( administrator = True )
async def clear(ctx, amount=None):
	await ctx.channel.purge(limit=int(amount))
	await ctx.channel.send(':: Сообщения успешно удалены ::')
	emb = discord.Embed(title = 'Все сделано в лучшем виде', colour=discord.Color.blue())
	emb.add_field(name = '✖Очистка', value = 'прошла успешно')

#econom


@client.command(aliases = ['casino', 'cs'])
async def __casino(ctx, amount: int = None):
	if amount == None:
		pass
	else:
		for row in cursor.execute(f"SELECT cash FROM users WHERE id={ctx.author.id}"):
			LVL = row[0]
			if amount > LVL:
				await ctx.send('У тебя недостаточно средств')
			else:
				a = random.randint(1,2)
				if a == 1:
					await ctx.send('Ты победил :moneybag:')
					LVL += amount
					cursor.execute(f"UPDATE users SET cash = {LVL} WHERE id = {ctx.author.id}")
					connection.commit()
				else:
					await ctx.send('Ты проиграл :moneybag:')
					LVL -= amount
					cursor.execute(f"UPDATE users SET cash = {LVL} WHERE id = {ctx.author.id}")
					embed = discord.Embed(title = f'**casino | {ctx.author.name}**', description = 'Результаты игры в casino' )
					embed.add_field(name = 'Ставка', value = f'```{amount}```')
					embed.add_field(name = 'Результ', value = '```Вы выйграли```', inline = False)
					embed.set_footer(text = f'Ваш баланс составляет: {cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone()[0]} :💰:')
					await ctx.send(embed = embed)
					connection.commit()
					

@client.command()
async def duel(ctx, member: discord.Member = None, amount: int = None ):
	a = random.randint(1, 2)
	if ctx.author == member:
		await ctx.send("С собой то вам зачем сражаться?")
		return
	if member is None:
		await ctx.send('укажите пользователя с которым хотите саревноваться')
	elif amount is None:
		await ctx.send('Укажите сумму за которую хотите биться!')
	elif amount > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
		await ctx.send(f'У вас не достаточно денег не балансе {PREFIX}cash!')
	elif amount > cursor.execute("SELECT cash FROM users WHERE id = {}".format(member.id)).fetchone()[0]:
		await ctx.send(f'На балансе вашего противника не хватает денег! {PREFIX}cash!')
	else:
		emb = discord.Embed(title = 'Бой', description = f'**Пользователь: {ctx.author.mention}, кинул вызов пользователю: {member.mention}!\n Бой начался!(ожидайте 5 секунд)**')
		await ctx.send(embed = emb)
		await asyncio.sleep(5)


		if a == 1:
			emb1 = discord.Embed(title = '**Итоги!**', description = f'**И так!\nВ этом бою побеждает....\n{ctx.author.mention}!!!!\nПоздравим! Он получает {amount}:💰:!**')
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
			connection.commit()
			await ctx.send( embed = emb1 )
		else:
			emb2 = discord.Embed(title = '**Итоги!**', description = f'**И так!\nВ этом бою побеждает....\n{member.mention}!!!!\nПоздравим! Он получает {amount}:💰:!**')
			cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
			connection.commit()
			await ctx.send( embed = emb2 )


@client.command(aliases =['монетка', 'bf'])
async def coin_flip(ctx, amount, arg):
	a = random.randint(0, 1)
	if a == 0:
		cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, ctx.author.id))
		connection.commit()
		embed = discord.Embed(title = f'**Орёл или Решка | {ctx.author.name}**', description = 'Результаты игры в орёл и решку' )
		embed.add_field(name = 'Ставка', value = f'```{amount}```')
		embed.add_field(name = 'Выбор', value = f'```{arg}```')
		embed.add_field(name = 'Результ', value = '```Вы выйграли```', inline = False)
		embed.set_footer(text = f'Ваш баланс составляет: {cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone()[0]} :💰:')
		await ctx.send(embed = embed)
	elif a == 1:
		cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))
		connection.commit()
		embed = discord.Embed(title = f'**Орёл или Решка | {ctx.author.name}**', description = 'Результаты игры в орёл и решку' )
		embed.add_field(name = 'Ставка', value = f'```{amount}```')
		embed.add_field(name = 'Выбор', value = f'```{arg}```')
		embed.add_field(name = 'Результ', value = '```Вы проиграли```', inline = False)
		embed.set_footer(text = f'Ваш баланс составляет: {cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchone()[0]} :💰:')
		await ctx.send(embed = embed)

#print('Logged on as {0}!'.format(self.user))

'''async def on_raw_reaction_add(self, payloada, user):
	chananel = self.get_channel(payloada.channel_id)  # получаем обьект канала
	message = await channel.fetch_message(payload.message_id) # получаем обьект сообщения
	member = utils.get(message.guild.member, id=payload.user_id) # получаем обьект пользователя который поставил реакцию

	try:
		emoji = str(payload.emoji) # эмоджик который выбрал юзер
		role = utils.get(message.guild.roles, id=config.Roles[emoji]) # обьект выбранной роли (если есть)

	if(len([i for i in member.roles if i.id not in config.EXCROLES]) <=config.MAX_ROLES_PER_USER):
		await member_roles(role)
		print('SUCCESS] User {0.display_name} has been granled with role {1.name}'.format)
	else:
	 await message.remove_reaction(payload.emoji, member)
	 print('[SUCCESS] Too many roles for user {0.display_name}'.format(member)'''


@client.command()
@commands.cooldown(1, 60*60*3, commands.BucketType.member)
async def rep(ctx, member: discord.Member = None):
	if member is None:
		await ctx.send(f'{ctx.author.mention}, вы не указали пользователя!')
	elif ctx.author == member:
		await ctx.send(f'{ctx.author.mention}, ты конечно извени но себе ты не сможешь дать репу!')
	else:
		cursor.execute("UPDATE users SET rep = rep + {} WHERE id = {}".format(1, member.id))
		connection.commit()
		emb = discord.Embed(title = '**Успешно!**', description = f"""У пользователя {member.name} была повышена репутация!\nТекущия репутация: {cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0]}🔺!""")
		await ctx.send(embed = emb)
 
		if cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0] == 20:
			cursor.execute("UPDATE users SET lvl = lvl + {} WHERE id = {}".format(1, member.id))
			connection.commit()
			await ctx.send(f'У пользователя {member.mention}, повыселcя уровень! Новый уровень: {cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}🔺')
 
		elif cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0] == 30:
			cursor.execute("UPDATE users SET lvl = lvl + {} WHERE id = {}".format(1, member.id))
			connection.commit()
			await ctx.send(f'У пользователя {member.mention}, повыселcя уровень! Новый уровень: {cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}🔺')
 
		elif cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0] == 40:
			cursor.execute("UPDATE users SET lvl = lvl + {} WHERE id = {}".format(1, member.id))
			connection.commit()
			await ctx.send(f'У пользователя {member.mention}, повыселcя уровень! Новый уровень: {cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}🔺')
 
		elif cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0] == 50:
			cursor.execute("UPDATE users SET lvl = lvl + {} WHERE id = {}".format(1, member.id))
			connection.commit()
			await ctx.send(f'У пользователя {member.mention}, повыселcя уровень! Новый уровень: {cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}🔺')
 
		elif cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0] == 60:
			cursor.execute("UPDATE users SET lvl = lvl + {} WHERE id = {}".format(1, member.id))
			connection.commit()
			await ctx.send(f'У пользователя {member.mention}, повыселcя уровень! Новый уровень: {cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}🔺')
 
		elif cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0] == 70:
			cursor.execute("UPDATE users SET lvl = lvl + {} WHERE id = {}".format(1, member.id))
			connection.commit()
			await ctx.send(f'У пользователя {member.mention}, повыселcя уровень! Новый уровень: {cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}🔺')
 
		elif cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0] == 80:
			cursor.execute("UPDATE users SET lvl = lvl + {} WHERE id = {}".format(1, member.id))
			connection.commit()
			await ctx.send(f'У пользователя {member.mention}, повыселcя уровень! Новый уровень: {cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}🔺')
 
		elif cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0] == 90:
			cursor.execute("UPDATE users SET lvl = lvl + {} WHERE id = {}".format(1, member.id))
			connection.commit()
			await ctx.send(f'У пользователя {member.mention}, повыселcя уровень! Новый уровень: {cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}🔺')
 
		elif cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0] == 100:
			cursor.execute("UPDATE users SET lvl = lvl + {} WHERE id = {}".format(1, member.id))
			connection.commit()
			await ctx.send(f'У пользователя {member.mention}, повыселcя уровень! Новый уровень: {cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]}🔺')

@client.command()
async def help(ctx):
	emb = discord.Embed(title = 'Все команды', colour=discord.Color.blue())
	emb.add_field(name = 'profile', value = '🤵Просмотр своего профиля')
	emb.add_field(name = 'user', value = '🤵Просмотр профиля друга')
	emb.add_field(name = 'report', value = '💼Жалоба на подсудимого')
	emb.add_field(name = '$, bal, balance', value = '🤑Баланс ваш или просмотр чужого баланса')
	emb.add_field(name = 'shop', value = '🛒Магазин')
	emb.add_field(name = 'work', value = '💳Работа за нее вам заплатят деньги от 500 до 5000 кд 10м')
	emb.add_field(name = 'bf', value = '💸Орёл или Рёшка игра ставка от 50')
	emb.add_field(name = 'cs, casino', value = '🎰Казино')
	emb.add_field(name = 'run', value = '🏎Вызов на гонку человека')
	emb.add_field(name = 'hug', value = '🤗Обнять человека')
	emb.add_field(name = 'kiss', value = '💋Поцелуй человека который нравиться')
	emb.add_field(name = 'buy', value = '🏦Покупка роли упаминание роли после команды')
	emb.add_field(name = 'rep', value = '🔺+Репутцаия чеовеку которого вы упамянули')
	emb.add_field(name = 'getrep', value = '🔺Посмотреть сколько репы у вас или у друга')
	emb.add_field(name = 'duel', value = '🤠Дуель с другом на сумму которую вы поставите!')
	await ctx.send(embed = emb)

@client.command()
@commands.has_permissions( administrator = True )
async def adm(ctx):
	emb = discord.Embed(title = 'Все команды administrator', colour=discord.Color.red())
	emb.add_field(name = 'add-shop', value = '🛍️Добавить роль в магаз, не забываейте упаминать роль')
	emb.add_field(name = 'remove-shop', value = '💈Удалить роль с магаза, не забываейте упаминать роль')
	emb.add_field(name = 'mute', value = '🤬Выдаеться мут в секундах')
	emb.add_field(name = 'clear', value = '✖Очистить чат не ограниченое каличество сообщений')
	emb.add_field(name = 'add', value = '💰Выдача денег')
	emb.add_field(name = 'take, t', value = '💰Забрать деньги')
	emb.add_field(name = 'temp_ban', value = '✔Бан')
	emb.add_field(name = 'unban', value = '✔Разбан')
	await ctx.send(embed = emb)



token = os.environ.get("BOT_TOKEN")

client.run( token )
