from cookiecutter.main import cookiecutter
import json
import os
from colorama import init as colorama_init
from colorama import Fore, Style
import sys
import tempfile
import click
import pytz

colorama_init()
RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
RESET = Style.RESET_ALL
BRIGHT = Style.BRIGHT
DIM = Style.DIM

TEMPLATE_DIR = "/template"
OUTPUT_DIR = "/out"

IS_PRODUCTION = os.path.isfile(os.path.join(TEMPLATE_DIR, "production-exclusives"))

BANNER = f"""{DIM}
╒══════════════════════════════════════════════════════════════════════════════╕
│                                                                              │
│         /$$                                         /$$                      │
│        | $$                                        | $$                      │
│        | $$  /$$$$$$  /$$   /$$ /$$$$$$$   /$$$$$$$| $$$$$$$   /$$$$$$       │
│        | $$ |____  $$| $$  | $$| $$__  $$ /$$_____/| $$__  $$ /$$__  $$      │
│        | $$  /$$$$$$$| $$  | $$| $$  \ $$| $$      | $$  \ $$| $$  \__/      │
│        | $$ /$$__  $$| $$  | $$| $$  | $$| $$      | $$  | $$| $$            │   
│        | $$|  $$$$$$$|  $$$$$$/| $$  | $$|  $$$$$$$| $$  | $$| $$            │    
│        |__/ \_______/ \______/ |__/  |__/ \_______/|__/  |__/|__/            │
│                                                                              │
╘══════════════════════════════════════════════════════════════════════════════╛
{RESET}""".strip()
BANNER = f"{BANNER}\n"


def press_enter():
    input(f"\nPress {BRIGHT}[Enter]{RESET} to continue")
    sys.stdout.write('\x1b[1A')
    sys.stdout.write('\x1b[2K')
    sys.stdout.write('\x1b[1A')
    sys.stdout.write('\x1b[2K')


def new():
    """
    Generates a new launchr project in the current working directory
    """
    print(
        f"{BANNER}"
        f"{BRIGHT}{GREEN}Good day{RESET}, {BRIGHT}{DIM}human entity{RESET}{BRIGHT}!{RESET}"
    )
    press_enter()
    print(
        f"I'm your very own personal assistant, guiding you through a couple of questions\n"
        f"before launching your project."
    )
    press_enter()
    print(
        f"You are probably pretty excited about your new idea but let's face it: We need \n"
        f"to sort a couple of things out, first!"
    )
    press_enter()
    print(
        f"If this is your first time with me, make sure to grab the handbook, available\n"
        f"here: {BRIGHT}https://launchr.io/docs/project-generation{RESET}"
    )
    press_enter()

    context = {
        "project_name": "",
        "project_slug": "",
        "author_name": "",
        "email": "",
        "domain_name": "domain.com",
        "location": "",
        "timezone": "",
        "private_beta": "n",
        "use_sentry": "y",
        "free_subscription_type": ["freemium", "trial", "None"]
    }

    # project name
    print(f"\nFirst things first, what's your {BRIGHT}project name{RESET} going to be?")
    context['project_name'] = click.prompt(f"{BRIGHT}Project name{RESET}", type=click.STRING)
    print(f"{GREEN}All right{RESET}, {DIM}{context['project_name']}{RESET} it's going to be!")
    press_enter()

    # project slug
    default_slug = context['project_name'].lower().replace(" ", "_").replace("-", "_").replace(".", "_").strip()
    print(
        f"\nNext, we need some sort of {BRIGHT}identifier{RESET} for your project.\n"
        f"I'm going to create a folder based on your {BRIGHT}identifier{RESET} and put all your \n"
        f"project files in there. Since we are using Python, this needs to be importable.\n"
        f"Based on your {DIM}project name{RESET}, how does {BRIGHT}{default_slug}{RESET} sound?"
    )
    # make sure the project_slug is valid
    while context['project_slug'] == "":
        context['project_slug'] = click.prompt(f"{BRIGHT}Identifier{RESET}", type=click.STRING, default=default_slug)
        invalid_chars = [" ", ".", "-"]
        for invalid_char in invalid_chars:
            if invalid_char in context['project_slug']:
                context['project_slug'] = ""
                print(f"{YELLOW}Nope{RESET}, this won't work. Your identifier contains a '{invalid_char}'."
                      f"Make sure your identifier has no ' ', '-', or '.' in it."
                      f"Let's try this again\n")
    context['project_slug'] = context['project_slug'].lower().strip()
    print(f"{GREEN}Ok{RESET}, {DIM}{context['project_slug']}{RESET} it is!")
    press_enter()

    # author name and email
    print(
        f"\nNow, a couple of personal details. I need your {BRIGHT}name{RESET} and {BRIGHT}email{RESET} to add\n"
        f"you as an admin in {DIM}config/settings/base.py{RESET}."
    )
    context['author_name'] = click.prompt(f"{BRIGHT}Name{RESET}", type=click.STRING)
    context['email'] = click.prompt(f"{BRIGHT}Email{RESET}", type=click.STRING)
    print(f"{GREEN}Nice{RESET} to meet you {DIM}{context['author_name']}{RESET}!")
    press_enter()

    # domain
    print(
        f"\nDo you already have a {BRIGHT}domain{RESET} name for your project?\n"
        f"If you don't have one yet, use the default {DIM}domain.com{RESET} and check \n"
        f"your personal handbook on how to change it later on."
    )
    context['domain_name'] = click.prompt(f"{BRIGHT}Domain{RESET}", type=click.STRING, default=context['domain_name'])
    print(f"{GREEN}Terrific{RESET}, your domain name is {DIM}{context['domain_name']}{RESET}")
    press_enter()

    # location
    print(
        f"\nWould you tell me the {BRIGHT}country{RESET} you are in?\n"
        f"I need this to fill out your sites terms of service."
    )
    context['location'] = click.prompt(f"{BRIGHT}Country{RESET}", type=click.STRING)
    print(f"{GREEN}Great{RESET}, so you live in {DIM}{context['location']}{RESET}!")
    press_enter()

    # timezone
    print(
        f"\nNext, I need to know about your {BRIGHT}timezone{RESET}.\n"
        f"I can print you a list of all available {BRIGHT}timezones{RESET} so you can choose \n"
        f"the one that's right for you.\n"
        "This is a long list, be prepared."
    )
    if click.confirm(f"Print out all {BRIGHT}timezones{RESET}?"):
        for tz in pytz.common_timezones:
            print(tz)
    context['timezone'] = click.prompt(f"{BRIGHT}timezone{RESET}", type=click.Choice(pytz.common_timezones),
                                       show_choices=False)
    print(f"{GREEN}Amazing{RESET}, {DIM}{context['timezone']}{RESET} must be a great timezone!")
    press_enter()

    # beta
    print(
        f"\nLet's get to something more interesting than timezones.\n"
        f"Are you planning to run a {BRIGHT}private beta{RESET}?\n"
        f"If you choose to run a {BRIGHT}private beta{RESET}, I can lock down your sites registration.\n"
        f"In order to sign up, people need to request an invite which you need to confirm."
    )
    context['private_beta'] = click.prompt(f"{BRIGHT}Private Beta{RESET}", type=click.Choice(["y", "n"]),
                                           default="n")
    print(f"{GREEN}Understood{RESET}", end=" ")
    if context['private_beta'] == "y":
        print(f"you {DIM}want{RESET} to run a {DIM}private beta{RESET}!")
    else:
        print(f"you {DIM}don't want{RESET} to run a {DIM}private beta{RESET}!")
    press_enter()

    # sentry
    print(
        f"\nLet's face it. Everyone makes errors. That's why we are human after all.\n"
        f"I can set up {BRIGHT}Sentry{RESET} to track all these errors for you automatically.\n"
        f"{BRIGHT}Sentry{RESET} is a third party service, but it's free for up to 5k errors per month."
    )
    context['use_sentry'] = click.prompt(f"{BRIGHT}Sentry{RESET}", type=click.Choice(["y", "n"]),
                                         default="n")
    print(f"{GREEN}Tremendous{RESET}", end=" ")
    if context['use_sentry'] == "y":
        print(f"you {DIM}want{RESET} to use {DIM}Sentry{RESET}!")
    else:
        print(f"you {DIM}don't want{RESET} to use {DIM}Sentry{RESET}!")
    press_enter()

    # subscription
    print(
        f"\nOkay, last question: {BRIGHT}subscriptions{RESET}.\n\n"
        f"Let's talk about what happens when a new user signs up to your service.\n"
        f"{BRIGHT}*{RESET} Do you want me to add the user to a {BRIGHT}trial{RESET} plan which \n"
        f"runs out automatically after a couple of days?\n"
        f"{BRIGHT}*{RESET} Do you want me to add the user to a limited {BRIGHT}freemium{RESET} plan?\n"
        f"{BRIGHT}*{RESET} Or do you want me to do {BRIGHT}None{RESET} of this?"
    )
    context['free_subscription_type'] = click.prompt(
        f"{BRIGHT}Subscription{RESET}", type=click.Choice(["freemium", "trial", "None"]),
        default="trial")
    print(f"{GREEN}That's huge{RESET}, so your choice for new users is", end=" ")
    if context['free_subscription_type'] in ["freemium", "trial"]:
        print(f"to subscribe them to a {DIM}{context['free_subscription_type']}{RESET} plan!")
    else:
        print(f"{DIM}None{RESET} at all!")

    print(f"\n\n{BRIGHT}I'm going to generate your project for you now{RESET}", end=" ")
    generated_dir = cookiecutter(
        template=TEMPLATE_DIR,
        no_input=True,
        extra_context=context,
        overwrite_if_exists=True,
        output_dir=OUTPUT_DIR
    )
    with open(os.path.join(generated_dir, "launchr.json"), "wt") as f:
        f.write(json.dumps(context))
    print(f"{BRIGHT}{GREEN}Done!{RESET}")
    press_enter()

    print(
        f"\nNow, go into your project directory and start your stack:\n\n"
        f"{BRIGHT}cd {context['project_slug']}{RESET}\n"
        f"{BRIGHT}docker-compose -f local.yml up{RESET}\n\n"
        f"This takes a couple of minutes the first time. Check out the getting started section \n"
        f"in the docs while you wait: {BRIGHT}https://launchr.io/docs/getting-started/{RESET}"
    )


def update():
    """
    Updates a launchr project
    """
    print(f"{BANNER}")
    try:
        with open(os.path.join(OUTPUT_DIR, "launchr.json"), "r") as f:
            context = json.loads(f.read())

            # create a cookiecutter template based on the context provided.
            # use a temporary directory, we are going to sync them later on
            temp_dir = tempfile.mkdtemp()
            cookiecutter(
                template=TEMPLATE_DIR,
                no_input=True,
                extra_context=context,
                overwrite_if_exists=False,
                output_dir=temp_dir
            )

            # some directories don't make sense to copy over
            omit_directories = []
            if click.prompt(
                "Exclude .env/ files? (Recommended)",
                default="y",
                type=click.BOOL
            ):
                omit_directories += [".env/"]

            if click.prompt(
                "Exclude template files? (Recommended)",
                default="y",
                type=click.BOOL
            ):
                omit_directories += ["templates/"]

            if click.prompt(
                "Exclude migration files? (Recommended)",
                default="y",
                type=click.BOOL
            ):
                omit_directories += ["migrations/"]

            if click.prompt(
                "Exclude test files? (Recommended)",
                default="y",
                type=click.BOOL
            ):
                omit_directories += ["tests/"]
            raise NotImplementedError

    except IOError:
        print(f"{RED}Error:{RESET} unable to find launchr.json in the project directory.")
        sys.exit(1)
    except ValueError:
        print(f"{RED}Error:{RESET} unable to load launchr.json. Make sure it is valid json.")
        sys.exit(1)


def upgrade():
    """
    upgrades a launchr project
    """
    raise NotImplementedError

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] in ['new', 'update', 'upgrade']:
        # run new, update or upgrade
        locals()[sys.argv[1]]()
    else:
        print("Usage: docker run -it [-v template_path:/template] -v ${PWD}:/out launchr [new|update|upgrade]")
        sys.exit(1)
