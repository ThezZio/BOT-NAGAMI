import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from datetime import timedelta
import re

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='+', intents=intents, help_command=None)

@bot.event
async def on_ready():
    if bot.user:
        print(f'✅ Bot connecté en tant que {bot.user}')
        print(f'ID: {bot.user.id}')
        print('------')
        await bot.change_presence(activity=discord.Game(name="Modération | +help"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)

@bot.command(name='help')
async def help_command(ctx):
    """Affiche toutes les commandes disponibles"""
    embed = discord.Embed(
        title="📋 Commandes de Modération",
        description="Voici toutes les commandes disponibles :",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🔇 Modération des utilisateurs",
        value=(
            "**+mute @user** - Mute un utilisateur (retire sa permission de parler)\n"
            "**+tempmute @user <durée> <raison>** - Mute temporaire (ex: +tempmute @user 10m spam)\n"
            "**+unmute @user** - Démute un utilisateur\n"
            "**+ban @user [raison]** - Bannit un utilisateur du serveur\n"
            "**+kick @user [raison]** - Expulse un utilisateur du serveur\n"
            "**+warn @user <raison>** - Avertit un utilisateur\n"
            "**+clear <nombre>** - Supprime un nombre de messages (max 100)"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🎭 Gestion des rôles",
        value=(
            "**+addr @user <ID_du_rôle>** - Ajoute un rôle à un utilisateur\n"
            "**+delr @user <ID_du_rôle>** - Retire un rôle à un utilisateur"
        ),
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Durées pour tempmute",
        value="s = secondes, m = minutes, h = heures, j = jours\nExemple: 30s, 5m, 2h, 1j",
        inline=False
    )
    
    embed.set_footer(text="Bot de modération")
    
    await ctx.send(embed=embed)

def parse_time(time_str):
    """Convertit une durée en secondes"""
    time_regex = re.match(r"(\d+)([smhj])", time_str.lower())
    if not time_regex:
        return None
    
    amount, unit = time_regex.groups()
    amount = int(amount)
    
    if unit == 's':
        return amount
    elif unit == 'm':
        return amount * 60
    elif unit == 'h':
        return amount * 3600
    elif unit == 'j':
        return amount * 86400
    return None

@bot.command(name='mute')
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, *, raison: str = "Aucune raison fournie"):
    """Mute un membre"""
    try:
        await member.timeout(timedelta(days=28), reason=raison)
        
        embed = discord.Embed(
            title="🔇 Membre muté",
            description=f"{member.mention} a été muté.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Raison", value=raison, inline=False)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
        try:
            await member.send(f"Vous avez été muté sur **{ctx.guild.name}**.\nRaison: {raison}")
        except:
            pass
            
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de mute ce membre.")
    except Exception as e:
        await ctx.send(f"❌ Une erreur s'est produite: {str(e)}")

@bot.command(name='tempmute')
@commands.has_permissions(moderate_members=True)
async def tempmute(ctx, member: discord.Member, duree: str, *, raison: str = "Aucune raison fournie"):
    """Mute temporairement un membre"""
    try:
        seconds = parse_time(duree)
        
        if seconds is None:
            await ctx.send("❌ Format de durée invalide. Utilisez: s (secondes), m (minutes), h (heures), j (jours)\nExemple: +tempmute @user 10m spam")
            return
        
        if seconds > 2419200:
            await ctx.send("❌ La durée maximale est de 28 jours (2419200 secondes).")
            return
        
        await member.timeout(timedelta(seconds=seconds), reason=raison)
        
        time_display = duree
        
        embed = discord.Embed(
            title="⏱️ Membre muté temporairement",
            description=f"{member.mention} a été muté pour {time_display}.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Raison", value=raison, inline=False)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
        try:
            await member.send(f"Vous avez été muté temporairement sur **{ctx.guild.name}** pour {time_display}.\nRaison: {raison}")
        except:
            pass
            
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de mute ce membre.")
    except Exception as e:
        await ctx.send(f"❌ Une erreur s'est produite: {str(e)}")

@bot.command(name='unmute')
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    """Démute un membre"""
    try:
        await member.timeout(None)
        
        embed = discord.Embed(
            title="🔊 Membre démuté",
            description=f"{member.mention} a été démuté.",
            color=discord.Color.green()
        )
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
        try:
            await member.send(f"Vous avez été démuté sur **{ctx.guild.name}**.")
        except:
            pass
            
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de démute ce membre.")
    except Exception as e:
        await ctx.send(f"❌ Une erreur s'est produite: {str(e)}")

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, raison: str = "Aucune raison fournie"):
    """Bannit un membre du serveur"""
    try:
        await member.ban(reason=raison)
        
        embed = discord.Embed(
            title="🔨 Membre banni",
            description=f"{member.mention} a été banni du serveur.",
            color=discord.Color.red()
        )
        embed.add_field(name="Raison", value=raison, inline=False)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
        try:
            await member.send(f"Vous avez été banni de **{ctx.guild.name}**.\nRaison: {raison}")
        except:
            pass
            
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de bannir ce membre.")
    except Exception as e:
        await ctx.send(f"❌ Une erreur s'est produite: {str(e)}")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, raison: str = "Aucune raison fournie"):
    """Expulse un membre du serveur"""
    try:
        await member.kick(reason=raison)
        
        embed = discord.Embed(
            title="👢 Membre expulsé",
            description=f"{member.mention} a été expulsé du serveur.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Raison", value=raison, inline=False)
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
        try:
            await member.send(f"Vous avez été expulsé de **{ctx.guild.name}**.\nRaison: {raison}")
        except:
            pass
            
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission d'expulser ce membre.")
    except Exception as e:
        await ctx.send(f"❌ Une erreur s'est produite: {str(e)}")

@bot.command(name='warn')
@commands.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, raison: str = "Aucune raison fournie"):
    """Avertit un membre"""
    embed = discord.Embed(
        title="⚠️ Avertissement",
        description=f"{member.mention} a reçu un avertissement.",
        color=discord.Color.yellow()
    )
    embed.add_field(name="Raison", value=raison, inline=False)
    embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
    
    await ctx.send(embed=embed)
    
    try:
        dm_embed = discord.Embed(
            title="⚠️ Avertissement",
            description=f"Vous avez reçu un avertissement sur **{ctx.guild.name}**.",
            color=discord.Color.yellow()
        )
        dm_embed.add_field(name="Raison", value=raison, inline=False)
        dm_embed.add_field(name="Modérateur", value=ctx.author.name, inline=False)
        await member.send(embed=dm_embed)
    except:
        await ctx.send("⚠️ Je n'ai pas pu envoyer de message privé à ce membre.")

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, nombre: int):
    """Supprime un nombre spécifique de messages dans le salon"""
    try:
        if nombre <= 0:
            await ctx.send("❌ Le nombre de messages doit être supérieur à 0.")
            return
        
        if nombre > 100:
            await ctx.send("❌ Vous ne pouvez pas supprimer plus de 100 messages à la fois.")
            return
        
        deleted = await ctx.channel.purge(limit=nombre + 1)
        
        embed = discord.Embed(
            title="🧹 Salon nettoyé",
            description=f"{len(deleted) - 1} message(s) supprimé(s).",
            color=discord.Color.green()
        )
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
        
        msg = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await msg.delete()
        
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de supprimer des messages dans ce salon.")
    except Exception as e:
        await ctx.send(f"❌ Une erreur s'est produite: {str(e)}")

@bot.command(name='addr')
@commands.has_permissions(manage_roles=True)
async def addr(ctx, member: discord.Member, role_id: str):
    """Ajoute un rôle à un membre"""
    try:
        role_id_int = int(role_id)
        role = ctx.guild.get_role(role_id_int)
        
        if not role:
            await ctx.send(f"❌ Aucun rôle trouvé avec l'ID `{role_id}`.")
            return
        
        if role in member.roles:
            await ctx.send(f"❌ {member.mention} possède déjà le rôle {role.mention}.")
            return
        
        await member.add_roles(role)
        
        embed = discord.Embed(
            title="✅ Rôle ajouté",
            description=f"Le rôle {role.mention} a été ajouté à {member.mention}.",
            color=discord.Color.green()
        )
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
    except ValueError:
        await ctx.send("❌ L'ID du rôle doit être un nombre valide.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission d'ajouter ce rôle.")
    except Exception as e:
        await ctx.send(f"❌ Une erreur s'est produite: {str(e)}")

@bot.command(name='delr')
@commands.has_permissions(manage_roles=True)
async def delr(ctx, member: discord.Member, role_id: str):
    """Retire un rôle à un membre"""
    try:
        role_id_int = int(role_id)
        role = ctx.guild.get_role(role_id_int)
        
        if not role:
            await ctx.send(f"❌ Aucun rôle trouvé avec l'ID `{role_id}`.")
            return
        
        if role not in member.roles:
            await ctx.send(f"❌ {member.mention} ne possède pas le rôle {role.mention}.")
            return
        
        await member.remove_roles(role)
        
        embed = discord.Embed(
            title="✅ Rôle retiré",
            description=f"Le rôle {role.mention} a été retiré à {member.mention}.",
            color=discord.Color.green()
        )
        embed.add_field(name="Modérateur", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
    except ValueError:
        await ctx.send("❌ L'ID du rôle doit être un nombre valide.")
    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas la permission de retirer ce rôle.")
    except Exception as e:
        await ctx.send(f"❌ Une erreur s'est produite: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    """Gestion des erreurs"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Membre introuvable. Assurez-vous de mentionner un membre valide.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument manquant. Utilisez `+help` pour voir la syntaxe correcte.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Argument invalide. Vérifiez votre commande.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"Erreur: {error}")

if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ ERREUR: Le token Discord n'est pas configuré.")
        print("Veuillez définir la variable d'environnement DISCORD_TOKEN.")
    else:
        try:
            bot.run(TOKEN)
        except discord.LoginFailure:
            print("❌ ERREUR: Token Discord invalide.")
        except Exception as e:
            print(f"❌ ERREUR lors du démarrage du bot: {e}")
