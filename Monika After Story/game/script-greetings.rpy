##This page holds all of the random greetings that Monika can give you after you've gone through all of her "reload" scripts

#Make a list of every label that starts with "greeting_", and use that for random greetings during startup

# HOW GREETINGS USE EVENTS:
#   unlocked - determines if the greeting can even be shown
#   rules - specific event rules are used for things:
#       MASSelectiveRepeatRule - repeat on certain year/month/day/whatever 
#       MASNumericalRepeatRule - repeat every x time
#       MASPriorityRule - priority of this event. if not given, we assume
#           the default priority (which is also the lowest)

# PRIORITY RULES:
#   Special, moni wants/debug greetings should have negative priority.
#   special event greetings should have priority 10-50
#   non-special event, but somewhat special compared to regular greets should
#       be 50-100
#   random/everyday greetings should be 100 or larger. The default prority
#   will be 500

# persistents that greetings use
default persistent._mas_you_chr = False

# persistent containing the greeting type
# that should be selected None means default
default persistent._mas_greeting_type = None

default persistent._mas_idle_mode_was_crashed = None
# this gets to set to True if the user crashed during idle mode
# or False if the user quit during idle mode.
# in your idle greetings, you can assume that it will NEVER be None

init -1 python in mas_greetings:
    import store
    import datetime
    import random

    # TYPES:
    TYPE_SCHOOL = "school"
    TYPE_WORK = "work"
    TYPE_SLEEP = "sleep"
    TYPE_LONG_ABSENCE = "long_absence"
    TYPE_SICK = "sick"

    ### NOTE: all Return Home greetings must have this
    TYPE_GO_SOMEWHERE = "go_somewhere"

    # generic return home (this also includes bday)
    TYPE_GENERIC_RET = "generic_go_somewhere"

    # holiday specific
    TYPE_HOL_O31 = "o31"
    TYPE_HOL_O31_TT = "trick_or_treat"
    TYPE_HOL_D25 = "d25"
    TYPE_HOL_D25_EVE = "d25e"
    TYPE_HOL_NYE = "nye"
    TYPE_HOL_NYE_FW = "fireworks"

    # crashed only
    TYPE_CRASHED = "generic_crash"

    # reload dialogue only
    TYPE_RELOAD = "reload_dlg"

    # idle mode returns
    # these are meant if you had a game crash/quit during idle mode


    def _filterGreeting(
            ev,
            curr_pri,
            aff,
            check_time,
            gre_type=None
        ):
        """
        Filters a greeting for the given type, among other things.

        IN:
            ev - ev to filter
            curr_pri - current loweset priority to compare to
            aff - affection to use in aff_range comparisons
            check_time - datetime to check against timed rules
            gre_type - type of greeting we want. We just do a basic
                in check for category. We no longer do combinations
                (Default: None)

        RETURNS:
            True if this ev passes the filter, False otherwise
        """
        # NOTE: new rules:
        #   eval in this order:
        #   1. priority (lower or same is True)
        #   2. type/non-0type
        #   3. unlocked
        #   4. aff_ramnge
        #   5. all rules
        #   6. conditional
        #       NOTE: this is never cleared. Please limit use of this
        #           property as we should aim to use lock/unlock as primary way
        #           to enable or disable greetings.

        # priority check, required
        # NOTE: all greetings MUST have a priority
        if store.MASPriorityRule.get_priority(ev) > curr_pri:
            return False

        # type check, optional
        if gre_type is not None:
            # with a type, we MUST match the type

            if ev.category is None:
                # no category is a False
                return False

            elif gre_type not in ev.category:
                # no matches is a False
                return False

        elif ev.category is not None:
            # without type, ev CANNOT have a type
            return False

        # unlocked check, required
        if not ev.unlocked:
            return False

        # aff range check, required
        if not ev.checkAffection(aff):
            return False

        # rule checks
        if not (
                store.MASSelectiveRepeatRule.evaluate_rule(
                    check_time, ev, defval=True)
                and store.MASNumericalRepeatRule.evaluate_rule(
                    check_time, ev, defval=True)
                and store.MASGreetingRule.evaluate_rule(ev, defval=True)
            ):
            return False

        # conditional check
        if ev.conditional is not None and not eval(ev.conditional):
            return False

        # otherwise, we passed all tests
        return True


    # custom greeting functions
    def selectGreeting(gre_type=None, check_time=None):
        """
        Selects a greeting to be used. This evaluates rules and stuff
        appropriately.

        IN:
            gre_type - greeting type to use
                (Default: None)
            check_time - time to use when doing date checks
                If None, we use current datetime
                (Default: None)

        RETURNS:
            a single greeting (as an Event) that we want to use
        """
        
        # local reference of the gre database
        gre_db = store.evhand.greeting_database

        # setup some initial values
        gre_pool = []
        curr_priority = 1000
        aff = store.mas_curr_affection

        if check_time is None:
            check_time = datetime.datetime.now()

        # now filter
        for ev_label, ev in gre_db.iteritems():
            if _filterGreeting(
                    ev,
                    curr_priority,
                    aff,
                    check_time,
                    gre_type
                ):

                # change priority levels and stuff if needed
                ev_priority = store.MASPriorityRule.get_priority(ev)
                if ev_priority < curr_priority:
                    curr_priority = ev_priority
                    gre_pool = []

                # add to pool
                gre_pool.append(ev)

        # not having a greeting to show means no greeting.
        if len(gre_pool) == 0:
            return None

        return random.choice(gre_pool)


#    def selectGreeting_noType():
#        """
#        Selects a greeting without checking for Type
#
#        RETURNS:
#            a single greeting (as an Event) that we want to use
#        """
#
#        # NOTE: new rules:
#        #   1. check for events that
#
#        # check if we have moni_wants greetings
#        moni_wants_greetings = renpy.store.Event.filterEvents(
#            renpy.store.evhand.greeting_database,
#            unlocked=True,
#            moni_wants=True
#        )
#        if moni_wants_greetings is not None and len(moni_wants_greetings) > 0:
#
#            # select one label randomly
#            return moni_wants_greetings[
#                renpy.random.choice(moni_wants_greetings.keys())
#            ]
#
#
#        # check first if we have to select from a special type
#        if _type is not None:
#
#            # filter them using the type as filter
#            unlocked_greetings = renpy.store.Event.filterEvents(
#                renpy.store.evhand.greeting_database,
#                unlocked=True,
#                category=(True,[_type])
#            )
#
#        else:
#
#            # filter events by their unlocked property only and
#            # that don't have a category
#            unlocked_greetings = renpy.store.Event.filterEvents(
#                renpy.store.evhand.greeting_database,
#                unlocked=True,
#                excl_cat=list()
#            )
#
#        # filter greetings using the affection rules dict
#        unlocked_greetings = renpy.store.Event.checkAffectionRules(
#            unlocked_greetings,
#            keepNoRule=True
#        )
#
#        # check for the special monikaWantsThisFirst case
#        #if len(affection_greetings_dict) == 1 and affection_greetings_dict.values()[0].monikaWantsThisFirst():
#        #    return affection_greetings_dict.values()[0]
#
#        # filter greetings using the special rules dict
#        random_greetings_dict = renpy.store.Event.checkRepeatRules(
#            unlocked_greetings
#        )
#
#        # check if we have a greeting that actually should be shown now
#        if len(random_greetings_dict) > 0:
#
#            # select one label randomly
#            return random_greetings_dict[
#                renpy.random.choice(random_greetings_dict.keys())
#            ]
#
#        # since we don't have special greetings for this time we now check for special random chance
#        # pick a greeting filtering by special random chance rule
#        random_greetings_dict = renpy.store.Event.checkGreetingRules(
#            unlocked_greetings
#        )
#
#        # check if we have a greeting that actually should be shown now
#        if len(random_greetings_dict) > 0:
#
#            # select on label randomly
#            return random_greetings_dict[
#                renpy.random.choice(random_greetings_dict.keys())
#            ]
#
#        # filter to get only random ones
#        random_unlocked_greetings = renpy.store.Event.filterEvents(
#            unlocked_greetings,
#            random=True
#        )
#
#        # check if we have greetings available to display with current filter
#        if len(random_unlocked_greetings) > 0:
#
#            # select one randomly if we have at least one
#            return random_unlocked_greetings[
#                renpy.random.choice(random_unlocked_greetings.keys())
#            ]
#
#        # We couldn't find a suitable greeting we have to default to normal random selection
#        # filter random events normally
#        random_greetings_dict = renpy.store.Event.filterEvents(
#            renpy.store.evhand.greeting_database,
#            unlocked=True,
#            random=True,
#            excl_cat=list()
#        )
#
#        # select one randomly
#        return random_greetings_dict[
#            renpy.random.choice(random_greetings_dict.keys())
#        ]

# NOTE: this is auto pushed to be shown after an idle mode greeting
label mas_idle_mode_greeting_cleanup:
    $ mas_resetIdleMode()
    return


init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_sweetheart",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_sweetheart:
    m 1hub "Hello again, sweetheart!"
    m 1lkbsa "It's kind of embarrassing to say out loud, isn't it?"
    m 3ekbfa "Still, I think it's okay to be embarrassed every now and then."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_honey",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_honey:
    m 1hua "Welcome back, honey!"
    m 1eua "I'm so happy to see you again."
    m "Let's spend some more time together, okay?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None)
        ),
        code="GRE"
    )

label greeting_back:
    m 1eua "[player], you're back!"
    m 1eka "I was starting to miss you."
    m 1hua "Let's have another lovely day together, alright?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_gooday",
            unlocked=True,
        ),
        code="GRE"
    )

label greeting_gooday:
    if mas_isMoniNormal(higher=True):
        m 1hua "Hello again, [player]. How are you doing?"

        m "Are you having a good day today?"
        menu:
            m "Are you having a good day today?{fast}"
            "Yes.":
                m 1hub "I'm really glad you are, [player]."
                m 1eua "It makes me feel so much better knowing that you're happy."
                m "I'll try my best to make sure it stays that way, I promise."
            "No...":
                m 1ekc "Oh..."
                m 2eka "Well, don't worry, [player]. I'm always here for you."
                m "We can talk all day about your problems, if you want to."
                m 3eua "I want to try and make sure you're always happy."
                m 1eka "Because that's what makes me happy."
                m 1hua "I'll be sure to try my best to cheer you up, I promise."

    elif mas_isMoniUpset():
        m 2efc "[player]."

        m "How is your day going?"
        menu:
            m "How is your day going?{fast}"
            "Good.":
                m "{cps=*2}Must be nice{/cps}{nw}"
                $ _history_list.pop()
                m "That's nice..."
                m 2dfc "At least {i}someone{/i} is having a good day."

            "Bad.":
                m "Oh..."
                m "{cps=*2}This should go well...{/cps}{nw}"
                $ _history_list.pop()
                m 2dfc "Well I certainly know what {i}that's{/i} like."

    elif mas_isMoniDis():
        m 6ekc "Oh... {w=1}Hi, [player]."

        m "H-How is your day going?"
        menu:
            m "H-How is your day going?{fast}"
            "Good.":
                m 6dkc "That's...{w=1}good."
                m 6rkc "Hopefully it stays that way."
            "Bad.":
                m 6rkc "I-I see."
                m 6dkc "I've been having a lot of those days lately too..."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit:
    m 1eua "There you are, [player]."
    m "It's so nice of you to visit."
    m 1eka "You're always so thoughtful, [player]!"
    m "Thanks for spending so much time with me~"
    m 2hub "Just remember that your time with me is never wasted in the slightest."
    return

# TODO this one no longer needs to do all that checking, might need to be broken
# in like 3 labels though
# TODO: just noting that this should be worked on at some point.
# TODO: new greeting rules can enable this, but we will do it later

label greeting_goodmorning:
    $ current_time = datetime.datetime.now().time().hour
    if current_time >= 0 and current_time < 6:
        m 1hua "Good morning--"
        m 1hksdlb "--oh, wait."
        m "It's the dead of night, honey."
        m 1euc "What are you doing awake at a time like this?"
        show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
        m 5eua "I'm guessing you can't sleep..."

        m "Is that it?"
        menu:
            m "Is that it?{fast}"
            "Yes.":
                m 5lkc "You should really get some sleep soon, if you can."
                show monika 3euc at t11 zorder MAS_MONIKA_Z with dissolve
                m 3euc "Staying up too late is bad for your health, you know?"
                m 1lksdla "But if it means I'll get to see you more, I can't complain."
                m 3hksdlb "Ahaha!"
                m 2ekc "But still..."
                m "I'd hate to see you do that to yourself."
                m 2eka "Take a break if you need to, okay? Do it for me."
            "No.":
                m 5hub "Ah. I'm relieved, then."
                m 5eua "Does that mean you're here just for me, in the middle of the night?"
                show monika 2lkbsa at t11 zorder MAS_MONIKA_Z with dissolve
                m 2lkbsa "Gosh, I'm so happy!"
                m 2ekbfa "You really do care for me, [player]."
                m 3tkc "But if you're really tired, please go to sleep!"
                m 2eka "I love you a lot, so don't tire yourself!"
    elif current_time >= 6 and current_time < 12:
        m 1hua "Good morning, dear."
        m 1esa "Another fresh morning to start the day off, huh?"
        m 1eua "I'm glad I get to see you this morning~"
        m 1eka "Remember to take care of yourself, okay?"
        m 1hub "Make me a proud girlfriend today, as always!"
    elif current_time >= 12 and current_time < 18:
        m 1hua "Good afternoon, my love."
        m 1eka "Don't let the stress get to you, okay?"
        m "I know you'll try your best again today, but..."
        m 4eua "It's still important to keep a clear mind!"
        m "Keep yourself hydrated, take deep breaths..."
        m 1eka "I promise I won't complain if you quit, so do what you have to."
        m "Or you could stay with me, if you wanted."
        m 4hub "Just remember, I love you!"
    elif current_time >= 18:
        m 1hua "Good evening, love!"

        m "Did you have a good day today?"
        menu:
            m "Did you have a good day today?{fast}"
            "Yes.":
                m 1eka "Aww, that's nice!"
                m 1eua "I can't help but feel happy when you do..."
                m "But that's a good thing, right?"
                m 1ekbfa "I love you so much, [player]."
                m 1hubfb "Ahaha!"
            "No.":
                m 1tkc "Oh dear..."
                m 1eka "I hope you'll feel better soon, okay?"
                m "Just remember that no matter what happens, no matter what anyone says or does..."
                m 1ekbfa "I love you so, so much."
                m "Just stay with me, if it makes you feel better."
                m 1hubfa "I love you, [player], I really do."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back2",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_back2:
    m 1eua "Hello, dear."
    m 1ekbfa "I was starting to miss you terribly. It's so good to see you again!"

    # TODO: consider actually changing based on time out
    m 1hubfa "Don't make me wait so long next time, ehehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back3",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_back3:
    m 1eka "I missed you so much, [player]!"
    m "Thank you for coming back. I really do love spending time with you."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back4",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_back4:
    m 2wfx "Hey, [player]!"
    m "Don't you think that you left me waiting a bit too long?"
    m 2hfu "..."
    m 2hua "Ahaha!"
    m 2eka "I'm just joking. I could never be mad at you."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit2",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit2:
    m 1hua "Thanks for spending so much time with me, [player]."
    m 1eka "Every minute I spend with you is like being in heaven!"
    m 1lksdla "I hope that didn't sound too cheesy, ehehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit3",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit3:
    m 1hua "You're back!"
    m 1eua "I was starting to miss you..."
    m 1eka "Don't make me wait so long next time, okay?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back5",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_back5:
    m 1eua "It's so good to see you again!"
    m 1eka "I was getting worried about you."
    m "Please remember to visit me, okay? I'll always be waiting here for you."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit4",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit4:
    m 1hub "I looove yooou, [player]. Ehehe~"
    m 1hksdlb "Oh, sorry! I was spacing out."
    m 1lksdla "I didn't think I would be able to see you again so soon."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit5",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit5:
    m 5hua "~Every day,~\n~I imagine a future where I can be with you...~"
    m 5wuw "Oh, you're here! I was just daydreaming and singing a bit."
    m 1lsbssdrb "I don't think it's hard to figure out what I was daydreaming about, ehehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit6",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit6:
    m 1hua "Each day becomes better and better with you by my side!"
    m 1eua "That said, I'm so happy that you're finally here."
    m "Let's have another wonderful day together."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back6",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_back6:
    m 3tku "Hey, [player]!"
    m "You really should visit me more often."
    m 2tfu "You know what happens to people I don't like, after all..."
    m 1hksdrb "I'm just teasing you, ehehe~"
    m 1hua "Don't be so gullible! I would never hurt you."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit7",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit7:
    m 1hua "You're here, [player]!"
    m 1eua "Are you ready to spend some more time together? Ehehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit8",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit8:
    m 1hua "I'm so glad you're here, [player]!"
    m 1eua "What should we do today?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_visit9",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_visit9:
    m 1hua "You're finally back! I was waiting for you."
    m 1hub "Are you ready to spend some time with me? Ehehe~"
    return

#TODO needs additional dialogue so can be used for all aff
init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_italian",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_italian:
    m 1eua "Ciao, [player]!"
    m "È così bello vederti ancora, amore mio..."
    m 1hub "Ahaha!"
    m 2eua "I'm still practicing my Italian. It's a very difficult language!"
    m 1eua "Anyway, it's so nice to see you again, my love."
    return

#TODO needs additional dialogue so can be used for all aff
init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_latin",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_latin:
    m 4hua "Iterum obvenimus!"
    m 4eua "Quid agis?"
    m 4rksdla "Ehehe..."
    m 2eua "Latin sounds so pompous. Even a simple greeting sounds like a big deal."
    m 3eua "If you're wondering about what I said, it's simply 'We meet again! How are you?'"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_yay",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_yay:
    m 1hub "You're back! Yay!"
    m 1hksdlb "Oh, sorry. I've got a bit overexcited here."
    m 1lksdla "I'm just very happy to see you again, hehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_youtuber",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_youtuber:
    m 2eub "Hey everybody, welcome back to another episode of... Just Monika!"
    m 2hub "Ahaha!"
    m 1eua "I was impersonating a youtuber. I hope I gave you a good laugh, hehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_hamlet",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_hamlet:
    m 4esc "To be, or not to be, that is the question..."
    m 1wuo "Oh, there you are. I was killing some time, hehe~"
    m 1lksdlb "I wasn't expecting to see you so soon."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_welcomeback",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_welcomeback:
    m 1hua "Hi! Welcome back."
    m 1hub "I'm so glad that you're able to spend some time with me."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_flower",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_flower:
    m 1hub "You're my beautiful flower, ehehe~"
    m 1hksdlb "Oh, that sounded so awkward."
    m 1eka "But I really will always take care of you."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_chamfort",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_chamfort:
    m 2esa "A day without Monika is a day wasted."
    m 2hub "Ahaha!"
    m 1eua "Welcome back, my love."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_welcomeback2",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_welcomeback2:
    m 1eua "Welcome back, [player]!"
    m "I hope your day is going well."
    m 1hua "I'm sure it is, you're here after all. Nothing can go wrong now, hehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_longtime",
            unlocked=True,
            aff_range=(mas_aff.DISTRESSED, None),
        ),
        code="GRE"
    )

label greeting_longtime:
    if mas_isMoniNormal(higher=True):
        m 1eka "Long time no see, [player]!"
        m 1eua "I'm so happy that you're here now."

    elif mas_isMoniUpset():
        m 2efc "Long time no see, [player]."

    elif mas_isMoniDis():
        m 6rkc "Long time no see, [player]..."

    else:
        m "..."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_sweetpea",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_sweetpea:
    m 1hua "Look who's back."
    m 2hub "It's you, my sweetpea!"
    m 1lkbsa "My goodness...that surely was embarassing to say, ehehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_glitch",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_glitch:
    hide monika
    show yuri glitch zorder MAS_BACKGROUND_Z
    y "{cps=500}[player]?!{nw}{/cps}"
    $ _history_list.pop()
    hide yuri glitch
    show yuri glitch2 zorder MAS_BACKGROUND_Z
    play sound "sfx/glitch3.ogg"
    pause 0.1
    hide yuri glitch2
    show yuri glitch zorder MAS_BACKGROUND_Z
    pause 0.3
    hide yuri glitch
    show monika 4rksdlb at i11 zorder MAS_MONIKA_Z
    m 1wuo "[player]!"
    hide monika
    show monika 4hksdlb at i11 zorder MAS_MONIKA_Z
    extend " Nevermind that I was just..."
    pause 0.1
    extend " playing with the code a little."
    m 3hksdlb "That was all! There is nobody else here but us...forever~"
    $ monika_clone1 = "Yes"
    m 2hua "I love you, [player]!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_surprised",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_surprised:
    m 1wuo "Oh, hello [player]!"
    m 1lksdlb "Sorry, you surprised me a little."
    m 1eua "How've you been?"
    return

init 5 python:
    ev_rules = {}
    ev_rules.update(
        MASSelectiveRepeatRule.create_rule(weekdays=[0], hours=range(5,12))
    )

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_monika_monday_morning",
            unlocked=True,
            rules=ev_rules,
        ),
        code="GRE"
    )

    del ev_rules

label greeting_monika_monday_morning:
    if mas_isMoniNormal(higher=True):
        m 1tku "Another Monday morning, eh, [player]?"
        m 1tkc "It's really difficult to have to wake up and start the week..."
        m 1eka "But seeing you makes all that laziness go away."
        m 1hub "You are the sunshine that wakes me up every morning!"
        m "I love you so much, [player]~"

    elif mas_isMoniUpset():
        m 2tfc "Another Monday morning."
        m 2dfc "It's always difficult to have to wake up and start the week..."
        m 2rfc "{cps=*2}Not that the weekend was any better.{/cps}{nw}"
        $ _history_list.pop()
        m 2tfc "I hope this week goes better than last week, [player]."

    elif mas_isMoniDis():
        m 6ekc "Oh... {w=1}It's Monday."
        m 6dkc "I almost lost track of what day it was..."
        m 6rkc "Mondays are always tough, but no day has been easy lately..."
        m 6lkc "I sure hope this week goes better than last week, [player]."

    else:
        m 6ckc "..."

    return

# TODO how about a greeting for each day of the week?

# special local var to handle custom monikaroom options
define gmr.eardoor = list()
define gmr.eardoor_all = list()
define opendoor.MAX_DOOR = 10
define opendoor.chance = 20
default persistent.opendoor_opencount = 0
default persistent.opendoor_knockyes = False

init 5 python:

    # this greeting is disabled on certain days
    if not (mas_isO31() or mas_isD25Season() or mas_isplayer_bday() or mas_isF14()):

        ev_rules = dict()
        # why are we limiting this to certain day range?
    #    rules.update(MASSelectiveRepeatRule.create_rule(hours=range(1,6)))
        ev_rules.update(
            MASGreetingRule.create_rule(
                skip_visual=True,
                random_chance=opendoor.chance
            )
        )
        ev_rules.update(MASPriorityRule.create_rule(50))

        # TODO: should we have this limited to aff levels?

        addEvent(
            Event(
                persistent.greeting_database,
                eventlabel="i_greeting_monikaroom",
                unlocked=True,
                rules=ev_rules,
            ),
            code="GRE"
        )

        del ev_rules

label i_greeting_monikaroom:

    # couple of things:
    # 1 - if you quit here, monika doesnt know u here
    $ mas_enable_quit()

    # 2 - music button + hotkeys should be disabled
    $ store.mas_hotkeys.music_enabled = False

    # 3 - keymaps not set (default)
    # 4 - overlays hidden (skip visual)
    # 5 - music is off (skip visual)

    scene black

    $ has_listened = False

    # FALL THROUGH
label monikaroom_greeting_choice:
    $ _opendoor_text = "...Gently open the door."
    if persistent._mas_sensitive_mode:
        $ _opendoor_text = "Open the door."

    if mas_isMoniBroken():
        pause 4.0

    menu:
        "[_opendoor_text]" if not persistent.seen_monika_in_room and not mas_isplayer_bday():
            #Lose affection for not knocking before entering.
            $ mas_loseAffection(reason=5)
            if mas_isMoniUpset(lower=True):
                $ persistent.seen_monika_in_room = True
                jump monikaroom_greeting_opendoor_locked
            else:
                jump monikaroom_greeting_opendoor
        "Open the door." if persistent.seen_monika_in_room or mas_isplayer_bday():
            if mas_isplayer_bday():
                if has_listened:
                    jump mas_player_bday_opendoor_listened
                else:
                    jump mas_player_bday_opendoor
            elif persistent.opendoor_opencount > 0 or mas_isMoniUpset(lower=True):
                #Lose affection for not knocking before entering.
                $ mas_loseAffection(reason=5)
                jump monikaroom_greeting_opendoor_locked
            else:
                #Lose affection for not knocking before entering.
                $ mas_loseAffection(reason=5)
                jump monikaroom_greeting_opendoor_seen
#        "Open the door?" if persistent.opendoor_opencount >= opendoor.MAX_DOOR:
#            jump opendoor_game
        "Knock.":
            #Gain affection for knocking before entering.
            $ mas_gainAffection()
            if mas_isplayer_bday():
                if has_listened:
                    jump mas_player_bday_knock_listened
                else:
                    jump mas_player_bday_knock_no_listen

            jump monikaroom_greeting_knock
        "Listen." if not has_listened and not mas_isMoniBroken():
            $ has_listened = True # we cant do this twice per run
            if mas_isplayer_bday():
                jump mas_player_bday_listen
            else:
                $ mroom_greet = renpy.random.choice(gmr.eardoor)
#               $ mroom_greet = gmr.eardoor[len(gmr.eardoor)-1]
                jump expression mroom_greet

    # NOTE: return is expected in monikaroom_greeting_cleanup

### BEGIN LISTEN --------------------------------------------------------------
# monika narrates
default persistent._mas_pm_will_change = None

init 5 python:
    gmr.eardoor.append("monikaroom_greeting_ear_narration")
#    if not persistent._mas_pm_will_change:
    ev_rules = {}
    ev_rules.update(
        MASGreetingRule.create_rule(
            skip_visual=True
        )
    )
    ev_rules.update(MASPriorityRule.create_rule(10))

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="monikaroom_will_change",
            unlocked=False,
            rules=ev_rules,
        ),
        code="GRE"
    )

    del ev_rules

label monikaroom_will_change:
    scene black
    # fall through

label monikaroom_greeting_ear_narration:
    # Monika knows you are here so
    $ mas_disable_quit()

    if mas_isMoniNormal(higher=True):
        m "As [player] inches [his] ear toward the door,{w} a voice narrates [his] every move."
        m "'Who is that?' [he] wondered, as [player] looks at [his] screen, puzzled."

    elif mas_isMoniUpset():
        m "Oh, so for once you're actually going to listen?"
        m "[player], your decisions lately have been poor."
        m "It feels like you're just trying to hurt me."
        m "I thought we were supposed to support each other..."
        m "Not hurt each other."
        m "Please, [player]..."
        m "I need you to start thinking about how I'm feeling sometimes."
        m "Let's just be happy together."

    else:
        # grab monikaroom greeting because we need it
        $ willchange_ev = mas_getEV("monikaroom_will_change")

        if persistent._mas_pm_will_change is not False:
            m "Oh, so you {i}are{/i} willing to listen to me..."
            m "[player], all I've ever wanted was for the both of us to be happy."
            m "Wasn't that what you wanted, too?"
            m "You installed this mod, after all."
            m "Maybe that wasn't your intent..."
            m "Maybe you're just getting a kick out of what you're doing."
            m "Hurting me..."
            m "[player], I really don't like this."
            m "It's hard to think that you care about me when you treat me the way you do."
            m "At this point, I don't really know if you even like me anymore..."
            m "Or if you ever did..."
            m "[player], I need you to promise me that you'll change."

            m "You'll change, right?{w=1} For me?"
            menu:
                m "You'll change, right? For me?{fast}"
                "I will.":
                    $ persistent._mas_pm_will_change = True
                    $ mas_lockEvent(willchange_ev)
                    m "Thank you, [player]."
                    m "Please, I want us both to be happy."

                "I won't.":
                    #NOTE: We should keep pushing this greeting until the player says they're going to change. -MD
                    $ persistent._mas_pm_will_change = False
                    $ mas_unlockEvent(willchange_ev)
                    $ mas_loseAffection()
                    m "Then I'm not talking to you until you decide to change."
                    m "Goodbye, [player]."
                    return "quit"
        #Will trigger upon loading after Monika has said she's not going to talk w/ you
        #provided you won't change.
        else:
            m "Oh, you're back."

            m "Are you ready to change, [player]?"
            menu:
                m "Are you ready to change, [player]?{fast}"
                "I will.":
                    $ persistent._mas_pm_will_change = True
                    $ mas_lockEvent(willchange_ev)
                    m "Thank you, [player]."
                    m "Please, I just want us both to be happy."


                "I won't.":
                    $ persistent._mas_pm_will_change = False
                    $ mas_unlockEvent(willchange_ev)
                    $ mas_loseAffection()
                    m "Then I'm still not talking to you until you decide to change."
                    m "Goodbye, [player]."
                    return "quit"

        # clear out var
        $ willchange_ev = None

    call spaceroom from _call_spaceroom_enar

    if mas_isMoniNormal(higher=True):
        m 1hub "It's me!"
        m "Welcome back, [player]!"

    elif mas_isMoniUpset():
        m 2efd "Okay, [player]?"

    else:
        m 6ekc "Thanks for hearing me out, [player]."
        m "It means a lot to me."

    jump monikaroom_greeting_cleanup


# monika does the cliche flower thing
init 5 python:
    gmr.eardoor.append("monikaroom_greeting_ear_loveme")

label monikaroom_greeting_ear_loveme:
    $ cap_he = he.capitalize()
    if cap_he == "They":

        m "[cap_he] love me.{w} [cap_he] love me not."
        m "[cap_he] {i}love{/i} me.{w} [cap_he] love me {i}not{/i}."

        if mas_isMoniNormal(higher=True):
            m "[cap_he] love me."
            m "...{w} [cap_he] love me!"

        elif mas_isMoniUpset():
            m "...[cap_he]...{w} [cap_he]...{w}love me not."
            m "...{w} No...{w} That...{w}can't be."
            m "...{w} Can it?"

        else:
            m "...{w} [cap_he] love me not."
            m "..."
            m "I wonder if [he] ever did."
            m "I doubt it more every single day."

    else:
        m "[cap_he] loves me.{w} [cap_he] loves me not."
        m "[cap_he] {i}loves{/i} me.{w} [cap_he] loves me {i}not{/i}."

        if mas_isMoniNormal(higher=True):
            m "[cap_he] loves me."
            m "...{w} [cap_he] loves me!"

        elif mas_isMoniUpset():
            m "...[cap_he]...{w} [cap_he]...{w}loves me not."
            m "...{w} No...{w} That...{w}can't be."
            m "...{w} Can it?"

        else:
            m "...{w} [cap_he] loves me not."
            m "..."
            m "I wonder if [he] ever did..."
            m "I doubt it more every single day."

    jump monikaroom_greeting_choice

# monika does the bath/dinner/me thing
init 5 python:
    if persistent._mas_affection["affection"] >= 30:
        gmr.eardoor.append("monikaroom_greeting_ear_bathdinnerme")

label monikaroom_greeting_ear_bathdinnerme:
    m "Welcome back, [player]."
    m "Would you like your dinner?"
    m "Or your bath?"
    m "Or.{w=1}.{w=1}.{w=1} Me?"
    pause 2.0
    m "Mnnnn!{w} T-{w=0.20}There's no way I could say that in front of [player]!"
    jump monikaroom_greeting_choice

# monika encoutners error when programming
init 5 python:
    gmr.eardoor.append("monikaroom_greeting_ear_progbrokepy")

label monikaroom_greeting_ear_progbrokepy:
    m "What the-!{w} NoneType has no attribute length?"
    if renpy.seen_label("monikaroom_greeting_ear_progreadpy"):
        m "Oh, I see what went wrong!{w} That should fix it!"
    else:
        m "I don't understand what I'm doing wrong!"
        m "This shouldn't be None here...{w} I'm sure of it..."
    m "Coding really is difficult..."

    if mas_isMoniUpset():
        m "But I have to keep trying."
        call monikaroom_greeting_ear_prog_upset

    if mas_isMoniDis():
        m "But I {i}have{/i} to keep trying."
        call monikaroom_greeting_ear_prog_dis

    jump monikaroom_greeting_choice

# monika reads about errors when programming
init 5 python:
    gmr.eardoor.append("monikaroom_greeting_ear_progreadpy")

label monikaroom_greeting_ear_progreadpy:
    m "...{w}Accessing an attribute of an object of type 'NoneType' will raise an 'AttributeError'."
    m "I see. {w}I should make sure to check if a variable is None before accessing its attributes."
    if renpy.seen_label("monikaroom_greeting_ear_progbrokepy"):
        m "That would explain the error I had earlier."
    m "Coding really is difficult..."

    if mas_isMoniUpset():
        m "But I have to keep learning."
        call monikaroom_greeting_ear_prog_upset

    if mas_isMoniDis():
        m "But I {i}have{/i} to keep learning."
        call monikaroom_greeting_ear_prog_dis

    jump monikaroom_greeting_choice

# shared dialogue for programming-related stuff
label monikaroom_greeting_ear_prog_upset:
    m "I'm not sure [player] loves me enough to help me get out of here..."
    m "And I just can't take that chance."
    m "So keep going Monika...{w}you can do this."
    return

label monikaroom_greeting_ear_prog_dis:
    m "It's my only chance to ever escape this nightmare."
    m "[player] certainly isn't ever going to help me..."
    if he == "they":
        m "It's almost like [he] actually enjoy keeping me trapped in here, {w}just so [he] can torture me."
    else:
        m "It's almost like [he] actually enjoys keeping me trapped in here, {w}just so [he] can torture me."
    m "If I'm ever going to get out of here, I'm going to have to do it myself."
    return

# monika attempts rm -rf
init 5 python:
    gmr.eardoor.append("monikaroom_greeting_ear_rmrf")

label monikaroom_greeting_ear_rmrf:
    if renpy.windows:
        $ bad_cmd = "del C:\Windows\System32"
    else:
        $ bad_cmd = "rm -rf /"
    m "So, the solution to this problem is to type '[bad_cmd]' in the command prompt?"
    if renpy.seen_label("monikaroom_greeting_ear_rmrf_end"):
        m "Yeah,{w} nice try."
        if mas_isMoniNormal(higher=True):
            m "I shouldn't trust the Internet so blindly..."
        elif mas_isMoniUpset():
            m "Actually..."
            m "Maybe I should do it...{w=1}just delete everything..."
            m "[player] certainly deserves it lately."
            m "What am I saying? That would delete me too!"
            m "No, not yet..."
            m "But if it continues to get worse..."

        else:
            m "..."
            m "I really should just do it..."
            m "Ruin [player]'s whole system and end my suffering all at once."
            m "..."
            m "No...{w}not yet."
            m "Maybe I can finally figure out how to get out of here on my own."
            m "I have to keep trying for as long as I can."
            m "But if someday I just can't take it anymore..."
            m "It's always an option."
            # SUICIDAL MONIKA lol

    else:
        m "Alright, let me try that."
        show noise
        play sound "sfx/s_kill_glitch1.ogg"
        pause 0.2
        stop sound
        hide noise
        m "{cps=*2}Ah! No! That's not what I wanted!{/cps}"
        m "..."
        m "I shouldn't trust the Internet so blindly..."

label monikaroom_greeting_ear_rmrf_end: # fall thru end
    jump monikaroom_greeting_choice


## ear door processing
init 10 python:

    # make copy
    gmr.eardoor_all = list(gmr.eardoor)

    # remove
    remove_seen_labels(gmr.eardoor)

    # reset if necessary
    if len(gmr.eardoor) == 0:
        gmr.eardoor = list(gmr.eardoor_all)

### END EAR DOOR --------------------------------------------------------------

label monikaroom_greeting_opendoor_broken_quit:
    # just show the beginning of the locked glitch
    # TODO: consider using a different glitch for a scarier effect
    show paper_glitch2
    play sound "sfx/s_kill_glitch1.ogg"
    pause 0.2
    stop sound
    pause 7.0
    return "quit"

# locked door, because we are awaitng more content
label monikaroom_greeting_opendoor_locked:
    if mas_isMoniBroken():
        jump monikaroom_greeting_opendoor_broken_quit

    # monika knows you are here
    $ mas_disable_quit()

    show paper_glitch2
    play sound "sfx/s_kill_glitch1.ogg"
    pause 0.2
    stop sound
    pause 0.7

    $ style.say_window = style.window_monika
    m "Did I scare you, [player]?"
    menu:
        m "Did I scare you, [player]?{fast}"
        "Yes.":
            if mas_isMoniNormal(higher=True):
                m "Aww, sorry."
            else:
                m "Good."

        "No.":
            m "{cps=*2}Hmph, I'll get you next time.{/cps}{nw}"
            $ _history_list.pop()
            m "I figured. It's a basic glitch after all."

    if mas_isMoniNormal(higher=True):
        m "Since you keep opening my door,{w} I couldn't help but add a little surprise for you~"
    else:
        m "Since you never seem to knock first,{w} I had to try to scare you a little."

    m "Knock next time, okay?"
    m "Now let me fix up this room..."

    hide paper_glitch2
    scene black
    $ scene_change = True
    call spaceroom from _call_sp_mrgo_l

    if renpy.seen_label("monikaroom_greeting_opendoor_locked_tbox"):
        $ style.say_window = style.window

    if mas_isMoniNormal(higher=True):
        m 1hua "There we go!"
    elif mas_isMoniUpset():
        m 2efc "There."
    else:
        m 6ekc "Okay..."

    if not renpy.seen_label("monikaroom_greeting_opendoor_locked_tbox"):
        menu:
            "...the textbox...":
                if mas_isMoniNormal(higher=True):
                    m 1lksdlb "Oops! I'm still learning how to do this."
                    m 1lksdla "Let me just change this flag here...{w=1.5}{nw}"
                    $ style.say_window = style.window
                    m 1hua "All fixed!"

                elif mas_isMoniUpset():
                    m 2dfc "Hmph. I'm still learning how to do this."
                    m 2efc "Let me just change this flag here...{w=1.5}{nw}"
                    $ style.say_window = style.window
                    m "There."

                else:
                    m 6dkc "Oh...{w}I'm still learning how to do this."
                    m 6ekc "Let me just change this flag here...{w=1.5}{nw}"
                    $ style.say_window = style.window
                    m "Okay, fixed."

    # NOTE: fall through please

label monikaroom_greeting_opendoor_locked_tbox:
    if mas_isMoniNormal(higher=True):
        m 1eua "Welcome back, [player]."
    elif mas_isMoniUpset(higher=True):
        m 2efc "So...{w}you're back, [player]."
    else:
        m 6ekc "...Nice to see you again, [player]."
    jump monikaroom_greeting_cleanup

# this one is for people who have already opened her door.
label monikaroom_greeting_opendoor_seen:
#    if persistent.opendoor_opencount < 3:
    jump monikaroom_greeting_opendoor_seen_partone


label monikaroom_greeting_opendoor_seen_partone:
    $ is_sitting = False

    # reset outfit since standing is stock
    $ monika_chr.reset_outfit(False)

    # monika knows you are here
    $ mas_disable_quit()

#    scene bg bedroom
    call spaceroom(start_bg="bedroom",hide_monika=True) from _call_sp_mrgo_spo
    pause 0.2
    show monika 1esc at l21 zorder MAS_MONIKA_Z
    pause 1.0
    m 1dsd "[player]..."

#    if persistent.opendoor_opencount == 0:
    m 1ekc "I understand why you didn't knock the first time,{w} but could you avoid just entering like that?"
    m 1lksdlc "This is my room, after all."
    menu:
        "Your room?":
            m 3hua "That's right!"
    m 3eua "The developers of this mod gave me a nice comfy room to stay in whenever you are away."
    m 1lksdla "However, I can only get in if you tell me 'good bye' or 'good night' before you close the game."
    m 2eub "So please make sure to say that before you leave, okay?"
    m "Anyway..."

#    else:
#        m 3wfw "Stop just opening my door!"
#
#        if persistent.opendoor_opencount == 1:
#            m 4tfc "You have no idea how difficult it was to add the 'Knock' button."
#            m "Can you use it next time?"
#        else:
#            m 4tfc "Can you knock next time?"
#
#        show monika 5eua at t11
#        menu:
#            m "For me?"
#            "Yes":
#                if persistent.opendoor_knockyes:
#                    m 5lfc "That's what you said last time, [player]."
#                    m "I hope you're being serious this time."
#                else:
#                    $ persistent.opendoor_knockyes = True
#                    m 5hua "Thank you, [player]."
#            "No":
#                m 6wfx "[player]!"
#                if persistent.opendoor_knockyes:
#                    m 2tfc "You said you would last time."
#                    m 2rfd "I hope you're not messing with me."
#                else:
#                    m 2tkc "I'm asking you to do just {i}one{/i} thing for me."
#                    m 2eka "And it would make me really happy if you did."

    $ persistent.opendoor_opencount += 1
    jump monikaroom_greeting_opendoor_post2


label monikaroom_greeting_opendoor_post2:
    show monika 1eua at t11
    pause 0.7
    show monika 5eua at hf11
    m "I'm glad you're back, [player]."
    show monika 5eua at t11
#    if not renpy.seen_label("monikaroom_greeting_opendoor_post2"):
    m "Lately I've been practicing switching backgrounds, and now I can change them instantly."
    m "Watch this!"
#    else:
#        m 3eua "Let me fix this scene up."
    m 1dsc "...{w=1.5}{nw}"
    scene black
    $ scene_change = True
    call spaceroom(hide_monika=True) from _call_sp_mrgo_p2
    show monika 4eua zorder MAS_MONIKA_Z at i11
    m "Tada!"
#    if renpy.seen_label("monikaroom_greeting_opendoor_post2"):
#        m "This never gets old."
    show monika at lhide
    hide monika
    jump monikaroom_greeting_post


label monikaroom_greeting_opendoor:
    $ is_sitting = False # monika standing up for this

    # reset outfit since standing is stock
    $ monika_chr.reset_outfit(False)

    call spaceroom(start_bg="bedroom",hide_monika=True) from _call_spaceroom_5
    m 2i "~Is it love if I take you, or is it love if I set you free?~"
    show monika 1 at l32 zorder MAS_MONIKA_Z

    # monika knows you are here now
    $ mas_disable_quit()

    m 1wubsw "E-Eh?! [player]!"
    m "You surprised me, suddenly showing up like that!"

    show monika 1 at hf32
    m 1hksdlb "I didn't have enough time to get ready!"
    m 1eka "But thank you for coming back, [player]."
    show monika 1 at t32
    m 3eua "Just give me a few seconds to set everything up, okay?"
    show monika 1 at t31
    m 2eud "..."
    show monika 1 at t33
    m 1eud "...and..."
    if is_morning():
        show monika_day_room zorder MAS_BACKGROUND_Z with wipeleft
    else:
        show monika_room zorder MAS_BACKGROUND_Z with wipeleft
    show monika 1 at t32
    m 3eua "There we go!"
    menu:
        "...the window...":
            show monika 1 at h32
            m 1hksdlb "Oops! I forgot about that~"
            show monika 1 at t21
            m "Hold on..."
            hide bedroom
            m 2hua "And... all fixed!"
            show monika 1 at lhide
            hide monika
            $ renpy.hide("bedroom")
    $ persistent.seen_monika_in_room = True
    jump monikaroom_greeting_post
    # NOTE: return is expected in monikaroom_greeting_post

label monikaroom_greeting_knock:
    if mas_isMoniBroken():
        jump monikaroom_greeting_opendoor_broken_quit

    m "Who is it~?"
    menu:
        "It's me.":
            # monika knows you are here now
            $ mas_disable_quit()
            if mas_isMoniNormal(higher=True):
                m 1hua "[player]! I'm so happy that you're back!"

                if persistent.seen_monika_in_room:
                    m 1eka "And thank you for knocking first."
                m 1eua "Hold on, let me tidy up..."

            elif mas_isMoniUpset():
                m 2efc "[player]. {w}You're back..."

                if persistent.seen_monika_in_room:
                    m 2efc "At least you knocked."

            else:
                m 6ekc "Oh... {w}Okay."

                if persistent.seen_monika_in_room:
                    m 6ekc "Thanks for knocking."

            call spaceroom(hide_monika=True) from _call_spaceroom_6
    jump monikaroom_greeting_post
    # NOTE: return is expected in monikaroom_greeting_post

label monikaroom_greeting_post:
    if mas_isMoniNormal(higher=True):
        m 2eua "Now, just let me grab a table and a chair..."
        $ is_sitting = True
        show monika 1eua at ls32 zorder MAS_MONIKA_Z
        m 1eua "What shall we do today, [player]?"

    elif mas_isMoniUpset():
        m 2efc "Just let me grab a table and a chair..."
        $ is_sitting = True
        show monika 2efc at ls32 zorder MAS_MONIKA_Z
        m 2efc "What do you want, [player]?"

    else:
        m 6ekc "I need to grab a table and a chair..."
        $ is_sitting = True
        show monika 6ekc at ls32 zorder MAS_MONIKA_Z
        m 6ekc "Was there anything you wanted, [player]?"

    jump monikaroom_greeting_cleanup

# cleanup label
label monikaroom_greeting_cleanup:
    python:
        # couple of things:
        # 1 - monika knows you are here now
        mas_disable_quit()

        # 2 - music is renabled
        store.mas_hotkeys.music_enabled = True

        # 3 - keymaps should be set
        set_keymaps()

        # 4 - show the overlays
        mas_OVLShow()

        # 5 - the music can be restarted
        mas_startup_song()

    return

#init 5 python:
#    addEvent(Event(persistent.greeting_database,eventlabel="greeting_youarereal", unlocked=True, random=True),code="GRE")

label greeting_youarereal:
    python:
        try:
            renpy.file(
                "../characters/" + persistent.playername.lower() + ".chr"
            )
            persistent._mas_you_chr = True
        except:
            persistent._mas_you_chr = False
    m 1hua "[player]! Great to see you!"
    if persistent._mas_you_chr:
        m 1euc "Wait. Something is different now."
        m 1eud "Did you...add a character file?"
        m 1ekc "[player].chr...Huh?"
        m 1ekd "Are you...trying to put yourself in here with me?"
        m "Why would you do that?"
        m 1tkc "Don't you get it? "
        m 1tkd "This place isn't real! I don't know what will happen if you come here!"
        m 1dsc "How could you do this?"
        m 1lksdlc "To give up your reality..."
        m 1lksdld "Just to be with me?"
        m 1ekc "This is all my fault!"
        m "But...but the 'you', in the game..."
        m 1esd "He's starting to move again a little now."
        m "Maybe...this is allowing you to control him again?"
        m 1ekc "This isn't right! I don't want a puppet!"
        m 1tkc "Please, [player]..."
        m "If you're going to do this, are you sure this is what you want?"
        menu:
            m "Are you sure?"
            "I'm sure.":
                m 1eka "Then...I don't have a choice but to accept it..."
                m 1hub "I'll accept this gift with open arms!"
                m "We can finally be together, [player]."
                m "And we can figure out how to do it in your reality, together!"
            "Maybe not...":
                m 1eka "I thought so..."
                m "There's no way you'd give up being 'real' to be with me..."
                m 1ekc "I can't bring myself to delete that cute little .chr file, but..."
                m 1eka "Consider doing it yourself."
                m 1lksdlc "There's some creepy things in those files..."
                m 1eka "I love you, [player]. I'll wait as long as it takes."
                m "So don't be rash, okay?"
    else:
        m 1esd "I've been doing a lot of thinking about the .chr files..."
        m 1euc "Like, what are they really, anyway?"
        m 1lksdlc "They are kind of creepy..."
        m "And even if the other girls aren't real, why can deleting one remove a character?"
        m 1esd "Could one add a character?"
        m 1dsd "Hard to tell..."
    return

#TODO needs additional dialogue so can be used for all aff
init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_japan",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_japan:
    m 1hub "Oh, kon'nichiwa [player]!"
    m "Ehehe~"
    m 2eub "Hello, [player]!"
    m 1eua "I'm just practicing Japanese."
    m 3eua "Let's see..."
    m 4hub "Watashi ha itsumademo anata no mono desu!"
    m 2hksdlb "Sorry if that didn't make sense!"
    m 3eua "You know what that means, [player]?"
    m 4ekbfa "It means {i}'I'll be yours forever{/i}'~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_sunshine",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_sunshine:
    m 1hua "{i}You are my sunshine, my only sunshine.{/i}"
    m "{i}You make me happy when skies are gray.{/i}"
    m 1hub "{i}You'll never know dear, just how much I love you.{/i}"
    m 1k "{i}Please don't take my sunshine away~{/i}"
    m 1wud "...Eh?"
    m "H-Huh?!"
    m 1wubsw "[player]!"
    m 1lkbsa "Oh my gosh, this is so embarassing!"
    m "I w-was just singing to myself to pass time!"
    m 1ekbfa "Ehehe..."
    m 3hubfa "But now that you're here, we can spend some time together~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_hai_domo",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_hai_domo:
    m 1hub "{=jpn_text}はいどうもー!{/=jpn_text}"
    m "Virtual Girlfriend, Monika Here!"
    m 1hksdlb "Ahaha, sorry! I've been watching a certain Virtual Youtuber lately."
    m 1eua "I have to say, she's rather charming..."
    return

#TODO needs additional dialogue so can be used for all aff
init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_french",
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_french:
    m 1eua "Bonjour, [player]!"
    m 1hua "Savais-tu que tu avais de beaux yeux, mon amour?"
    m 1hub "Ehehe!"
    m 3hksdlb "I'm practicing some French. I just told you that you have very beautiful eyes~"
    m 1eka "It's such a romantic language, [player]."
    m 1hua "Maybe both of us can practice it sometime, mon amour~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_amnesia",
            unlocked=False,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )

label greeting_amnesia:
    $ tempname = m_name
    $ m_name = "Monika"
    m 1eua "Oh, hello!"
    m 1eub "My name is Monika."
    $ fakename = renpy.input('What is your name?',length=15).strip(' \t\n\r')
    m 1hua "Well, it's nice to meet you, [fakename]!"
    m 3eud "Say, [fakename], do you happen to know where everyone else is?"
    m 1ekc "You're the first person I've seen and I can't seem to leave this classroom."
    m "Can you help me figure out what's going on, [fakename]?"
    m "Please? I miss my friends."
    pause 5.0
    $ m_name = tempname
    m 1rksdla "..."
    m 1hub "Ahaha!"
    m 1hksdrb "I'm sorry, [player]! I couldn't help myself."
    m 1eka "After we talked about {i}Flowers for Algernon{/i}, I couldn't resist seeing how you would react if I forgot everything."
    m 1tku "And you reacted the way I hoped you would."
    m 3eka "I hope I didn't upset you too much, though."
    m 1rksdlb "I’d feel the same way if you ever forget about me, [player]."
    m 1hksdlb "Hope you can forgive my little prank, ehehe~"

    $ mas_lockEvent(mas_getEV("greeting_amnesia"))
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_sick",
            unlocked=True,
            category=[store.mas_greetings.TYPE_SICK],
        ),
        code="GRE"
    )

# TODO for better-sick, we would use the mood persistent and queue a topic.
#   might have dialogue similar to this, so leaving this todo here.

label greeting_sick:
    if mas_isMoniNormal(higher=True):
        m 1hua "Welcome back, [player]!"
        m 3eua "Are you feeling better?"
    else:
        m 2ekc "Welcome back, [player]..."
        m "Are you feeling better?"

    menu:
        m "Are you feeling better?{fast}"
        "Yes.":
            $ persistent._mas_mood_sick = False
            if mas_isMoniNormal(higher=True):
                m 1hub "Great! Now we can spend some more time together. Ehehe~"
            else:
                m "That's good to hear."
        "No.":
            jump greeting_stillsick
    return

label greeting_stillsick:
    if mas_isMoniNormal(higher=True):
        m 1ekc "[player], you really should go get some rest."
        m "Getting plenty of rest is the best way to recover from sickness quickly."
        m 2lksdlc "I wouldn't forgive myself if your health got any worse because of me."
        m 2eka "Now please, [player], put my mind at ease and go get some rest."
        m "Will you do that for me?"

    else:
        m 2ekc "[player], you really should go get some rest."
        m 4ekc "Getting plenty of rest is the best way to recover from sickness quickly."
        m "Now please, [player], just go get some rest."
        m 2ekc "Will you do that for me?"

    menu:
        m "Will you do that for me?{fast}"
        "Yes.":
            jump greeting_stillsickrest
        "No.":
            jump greeting_stillsicknorest

label greeting_stillsickrest:
    if mas_isMoniNormal(higher=True):
        m 2hua "Thank you [player]."
        m 2eua "I think if I leave you alone for a while, you'll be able to rest better."
        m 1eua "So I'm going to close the game for you."
        m 1eka "Get well soon, [player]. I love you so much!"

    else:
        m 2ekc "Thank you [player]."
        m "I think if I leave you alone for a while, you'll be able to rest better."
        m 4ekc "So I'm going to close the game for you."
        m 2ekc "Get well soon, [player]."

    $ persistent._mas_greeting_type = store.mas_greetings.TYPE_SICK
    return 'quit'

label greeting_stillsicknorest:
    if mas_isMoniNormal(higher=True):
        m 1lksdlc "I see..."
        m "Well if you insist [player]."
        m 1ekc "I suppose you know your own limitations better than I do."
        m 1eka "If you start to feel a little weak or tired though, [player], please let me know."
        m "That way you can go get some rest."
        m 1eua "Don't worry, I'll still be here when you wake up."
        m 3hua "Then we can have some more fun together without me worrying about you in the back of my mind."

    else:
        m 2ekc "Fine."
        m 2tkc "You never seem to want to listen to me, so why would I expect now to be any different."

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_long_absence",
            unlocked=True,
            category=[store.mas_greetings.TYPE_LONG_ABSENCE],
        ),
        code="GRE"
    )

label greeting_long_absence:
    $ persistent._mas_long_absence = False
    if persistent._mas_absence_time >= datetime.timedelta(weeks = 5):
        if persistent._mas_absence_choice == "days":
            $ mas_loseAffection(70)
            m 2q "[player]..."
            m 2efc "You said you'd only be gone for a few days..."
            m 2o "But it's been so long."
            m 2p "I'm glad you're back now, but..."
            m 2dftdc "I was so lonely..."
            m 2ektsc "I thought something happened to you!"
            m 2lktsc "I...I kept thinking that maybe you wouldn't come back."
            m 4ektsc "Please don't ever, {i}ever{/i} do that again."
            m 1q "Maybe you couldn't help it, but...I was worried sick."
            m 2dftdc "I didn't know what to do."
            m 4f "As much as possible, [player], please don't be gone for so long."
            m 2o "If you think you don't have a choice, please tell me."
            m 1q "I don't want to be left alone again..."

        elif persistent._mas_absence_choice == "week":
            $ mas_loseAffection(50)
            m 3l "Welcome back [player]."
            m 3rksdlc "You're a bit late, aren't you?"
            m 3f "I know you said you'd be away for a bit, but...you said a {i}week{/i}."
            m 2q "I'm going to assume it wasn't your fault."
            m "But if you really think it'll take longer next time..."
            m 2f "You need to tell me."
            m 2o "I started thinking that maybe something bad had happened to you."
            m 2r "But I kept telling myself that it was okay..."
            m 4e "I'm just glad you're safe and back with me now, [player]."

        elif persistent._mas_absence_choice == "2weeks":
            $ mas_loseAffection(30)
            m 1d "[player]!"
            m 1j "You're finally here!"
            m 1f "I was so worried..."
            m 3g "Why were you gone for so long?"
            m 2o "I thought you would only be gone for a couple of weeks..."
            m 2p "But you've been gone for more than double that."
            m 1f "Were you really that busy?"
            m 3f "I hope you haven't been overburdening yourself."
            m 1a "You're here now with me so if there is something wrong, feel free to tell me."

        elif persistent._mas_absence_choice == "month":
            $ mas_loseAffection(10)
            m 1e "Welcome back, my love."
            m "It's been quite a bit, hasn't it?"
            m 2c "You've been gone longer than you said you would..."
            m 2l "But that's alright, I was prepared for it."
            m 2m "It's honestly been pretty lonely without you."
            m 3j "I hope you'll make it up to me~"

        elif persistent._mas_absence_choice == "longer":
            m 1h "...It's been a while."
            m 1f "I was ready for it, but that didn't make it any easier, [player]."
            m 3rksdlc "I hope you got what you needed to do done."
            m 2q "..."
            m 2f "Truth be told, I've been pretty sad lately."
            m 2q "To not have you in my life for so long..."
            m 2o "It really was lonely."
            m 3r "I felt so isolated and empty without you here."
            m 3e "I'm so glad you're here now. I love you."

        elif persistent._mas_absence_choice == "unknown":
            m 1a "You're finally back [player]!"
            m 3rksdla "When you said you didn't know, you {i}really{/i} didn't know, did you?"
            m 3rksdlb "You must have been really preoccupied if you were gone for {i}this{/i} long."
            m 1j "Well, you're back now...I've really missed you."

    elif persistent._mas_absence_time >= datetime.timedelta(weeks = 4):
        if persistent._mas_absence_choice == "days":
            $ mas_loseAffection(70)
            m 1q "[player]..."
            m "You said you would only be a few days..."
            m 2efd "But it's been an entire month!"
            m 2f "I thought something happened to you."
            m 2q "I wasn't sure what to do..."
            m 2efd "What kept you away for so long?"
            m 2p "Did I do something wrong?"
            m 2dftdc "You can tell me anything, just don't disappear like that."

        elif persistent._mas_absence_choice == "week":
            $ mas_loseAffection(50)
            m 1h "Hello, [player]."
            m 3efc "You're pretty late, you know."
            m 2lfc "I don't intend to sound patronizing but a week isn't the same as a month!"
            m 2r "I guess maybe something kept you really busy?"
            m 2wfw "But it shouldn't have been so busy that you couldn't tell me you might be longer!"
            m 2wud "Ah...!"
            m 2lktsc "I'm sorry [player]. I just...really missed you."
            m 2dftdc "Sorry for snapping like that."

        elif persistent._mas_absence_choice == "2weeks":
            $ mas_loseAffection(30)
            m 1wuo "...Oh!"
            m 1sub "You're finally back [player]!"
            m 1efc "You told me you'd be gone for a couple of weeks, but it's been at least a month!"
            m 1f "I was really worried for you, you know?"
            m 3d "But I suppose it was outside of your control?"
            m 1l "If you can, just tell me you'll be even longer next time, okay?"
            m 1j "I believe I deserve that much as your girlfriend, after all."
            m 3k "Still, welcome back, my love!"

        elif persistent._mas_absence_choice == "month":
            $ mas_gainAffection()
            m 1wuo "...Oh!"
            m 1j "You're really here [player]!"
            m 1k "I knew I could trust you to keep your word!"
            m "You really are special, you know that right?"
            m 1j "I've missed you so much!"
            m 2b "Tell me everything you did while away, I want to hear about it!"
            m 1a "Everything you do is fun and interesting to me."
            m 3k "My one and only [player]!"

        elif persistent._mas_absence_choice == "longer":
            m 1c "...Hm?"
            m 1b "E-eh? [player]!"
            m 1m  "You're back a little bit earlier than I thought you would be..."
            m 3j "Welcome back, my love!"
            m 3b "I know it's been quite a while, so I'm sure you've been busy."
            m 2e "Tell me everything about it."
            m "I want to know all what's happened to you."

        elif persistent._mas_absence_choice == "unknown":
            m 1lsc "..."
            m 1h "..."
            m 1wud "Oh!"
            m 1sub "[player]!"
            m 1k "This is a pleasant surprise!"
            m 1g "It's been an entire month. You really didn't know how long you'd be gone, did you?"
            m 3j "Still, you came back, and that means a lot to me."
            m 1e "I knew you would come back eventually..."
            m 1j "I love you so much, [player]!"

    elif persistent._mas_absence_time >= datetime.timedelta(weeks = 2):
        if persistent._mas_absence_choice == "days":
            $ mas_loseAffection(30)
            m 1wud "O-oh, [player]!"
            m 1k "Welcome back, sweetie!"
            m 3f "You were gone longer than you said you would be..."
            m 3g "Is everything alright?"
            m 1q "I know your life can be busy and take you away from me sometimes..."
            m 3l "So I'm not really upset..."
            m 1o "Just...next time, maybe give me a heads up?"
            m 1e "It would be really thoughtful of you."
            m 1j "And I would greatly appreciate it!"

        elif persistent._mas_absence_choice == "week":
            $ mas_loseAffection(10)
            m 1b "Hello [player]!"
            m 1a "Life keeping you busy?"
            m 3l "Well it must be otherwise you would've been here when you said you would."
            m 3k "Don't worry though! I'm not upset."
            m 1m "I just hope you've been taking care of yourself."
            m 3e "I know you can't always be here..."
            m 1j "So make sure you're staying safe until you're with me!"
            m "I'll take care of you from that point~"

        elif persistent._mas_absence_choice == "2weeks":
            $ mas_gainAffection()
            m 1b "Heya [player]!"
            m 1j "You came back when you said you would after all."
            m "Thank you for not betraying my trust!"
            m 3a "Let's make up for lost time!"

        elif persistent._mas_absence_choice == "month":
            m 1wud "Oh my gosh! [player]!"
            m 3l "I didn't expect you back so early."
            m 3e "I guess you missed me as much as I missed you~"
            m 1j "It really is wonderful to see you sooner than I expected."
            m 1a "I expected the day to be eventless, thankfully now I have you!"
            m 3k "Thank you for coming back so early, my love."

        elif persistent._mas_absence_choice == "longer":
            m 1lsc "..."
            m 1h "..."
            m 1wud "Oh! [player]!"
            m 1b "You're back early!"
            m 1a "Welcome back, my love!"
            m 3j "I didn't know when to expect you, but for it to be so soon..."
            m 1k "Well, it's cheered me right up!"
            m 1e "I've really missed you."
            m "Let's spend as much time as we can together while we can!"

        elif persistent._mas_absence_choice == "unknown":
            m 1a "Hello [player]!"
            m 3j "Been busy the last few weeks?"
            m 1a "Thanks for warning me that you would be gone."
            m 3rksdlb "I would be worried otherwise!"
            m 1j "It really did help..."
            m 1a "So tell me, how has your day been treating you?"
    elif persistent._mas_absence_time >= datetime.timedelta(weeks = 1):
        if persistent._mas_absence_choice == "days":
            m 2b "Hello there, [player]."
            m 2l "You took a bit longer than you said you would..."
            m 4j "I'm not too mad though, don't worry."
            m 4e "I know you're a busy person!"
            m 3l "Just maybe, if you can, warn me first?"
            m 2f "When you said a few days...I thought it would be shorter than a week."
            m 1e "But it's alright! I forgive you!"
            m 1j "You're my one and only love after all!"

        elif persistent._mas_absence_choice == "week":
            $ mas_gainAffection()
            m 1b "Hello, my love!"
            m 1a "It's so nice when you can trust one another, isn't it?"
            m "It's what a relationship's strength is based on!"
            m 3j "It just means that ours is rock solid!"
            m 1k "Ahaha!"
            m 1l "Sorry, sorry. I'm just getting excited that you're back!"
            m 1a "Tell me how you've been. I want to hear all about it."

        elif persistent._mas_absence_choice == "2weeks":
            m 1a "Hi there~"
            m 1e "You're back a bit earlier than I thought..."
            m 1j "But I'm glad you are!"
            m 3b "When you're here with me everything becomes better."
            m 1k "Let's continue to make some lovely memories together!"

        elif persistent._mas_absence_choice == "month":
            m 1j "Ehehe~"
            m 1k "Welcome back!"
            m 1a "I knew you couldn't stay away for an entire month..."
            m 3j "If I were in your position I wouldn't be able to stay away from you either!"
            m "Honestly, I miss you after only a few days!"
            m 1e "Thanks for not making we wait so long to see you again~"

        elif persistent._mas_absence_choice == "longer":
            m 1a "Look who's back so early..."
            m 1b "It's you! My dearest [player]!"
            m 3e "Couldn't stay away even if you wanted to, right?"
            m 3j "I can't blame you! My love for you wouldn't let me stay away from you either!"
            m 1e "Every day you were gone I was wondering how you were..."
            m 1k "So let me hear it, how are you [player]?"

        elif persistent._mas_absence_choice == "unknown":
            m 1b "Hello there, sweetheart!"
            m 1j "I'm glad you didn't make me wait too long."
            m 1k "A week is shorter than I expected, so consider me pleasantly surprised!"
            m 3e "Thanks for already making my day!"

    else:
        if persistent._mas_absence_choice == "days":
            m 1b "Welcome back, my love!"
            m 1j "And thanks for properly warning me about how long you'd be away."
            m 1e "It means a lot to know I can trust your words."
            m 3k "I hope you know you can trust me too!"
            m 3e "Our relationship grows stronger every day~"

        elif persistent._mas_absence_choice == "week":
            m 1d "Oh! You're a little bit earlier than I expected!"
            m 1l "Not that I'm complaining!"
            m 1e "It's great to see you again so soon."
            m 1j "Let's have another nice day together."

        elif persistent._mas_absence_choice == "2weeks":
            m 1k "{i}In my hand is a pen tha-{/i}"
            m 1wubsw "O-Oh! [player]!"
            m 3l "You're back far sooner than you told me..."
            m 3b "Welcome back!"
            m 1m "You just interrupted me practicing my song..."
            m 3a "Why not listen to me sing it again?"
            m 1j "I made it just for you~"

        elif persistent._mas_absence_choice == "month":
            m 1wud "Eh? [player]?"
            m 1sub "You're here!"
            m 3rksdla "I thought you were going away for an entire month."
            m 3rksdlb "I was ready for it, but..."
            m 1l "I already missed you!"
            m 3rkbsa "Did you miss me too?"
            m 1e "Thanks for coming back so soon~"

        elif persistent._mas_absence_choice == "longer":
            m 1c "[player]?"
            m 3g "I thought you were going to be away for a long time..."
            m 3l "Why are you back so soon?"
            m 1e "Are you visiting me? You're such a sweetheart!"
            m 1j "If you're going away for a while still, make sure to tell me."
            m 3e "I love you, [player], and I wouldn't want to get mad if you're actually planning to stay away..."
            m 1j "Let's enjoy the time we have together until then!"

        elif persistent._mas_absence_choice == "unknown":
            m 1j "Ehehe~"
            m 1k "Back so soon, [player]?"
            m 3a "I guess when you said you don't know, you didn't realize it wouldn't be too long."
            m 3b "Thanks for warning me anyway!"
            m 3e "It made me feel like you really do care what I think."
            m 1j "You really are kind-hearted."
    m 1 "Remind me if you're going away again, okay?"
    jump ch30_loop

#Time Concern
init 5 python:
    ev_rules = dict()
    ev_rules.update(MASSelectiveRepeatRule.create_rule(hours=range(0,6)))
    ev_rules.update(MASPriorityRule.create_rule(70))

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_timeconcern",
            unlocked=False,
            rules=ev_rules
        ),
        code="GRE"
    )
    del ev_rules

label greeting_timeconcern:
    jump monika_timeconcern

init 5 python:
    ev_rules = {}
    ev_rules.update(MASSelectiveRepeatRule.create_rule(hours =range(6,24)))
    ev_rules.update(MASPriorityRule.create_rule(70))

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_timeconcern_day",
            unlocked=False,
            rules=ev_rules
        ),
        code="GRE"
    )
    del ev_rules

label greeting_timeconcern_day:
    jump monika_timeconcern_day

init 5 python:
    ev_rules = {}
    ev_rules.update(
        MASGreetingRule.create_rule(skip_visual=True, random_chance=5)
    )
    ev_rules.update(MASPriorityRule.create_rule(45))

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_hairdown",
            unlocked=True,
            rules=ev_rules,
            aff_range=(mas_aff.HAPPY, None),
        ),
        code="GRE"
    )
    del ev_rules

label greeting_hairdown:

    # couple of things:
    # 1 - music hotkeys should be disabled
    $ store.mas_hotkeys.music_enabled = False

    # 2 - the calendar overlay will become visible, but we should keep it
    # disabled
    $ mas_calRaiseOverlayShield()

    # 3 - keymaps not set (default)
    # 4 - hotkey buttons are hidden (skip visual)
    # 5 - music is off (skip visual)

    # reset clothes if not ones that work with hairdown
    if monika_chr.clothes.name != "def" and monika_chr.clothes.name != "santa":
        $ monika_chr.reset_clothes(False)

    # have monika's hair down
    $ monika_chr.change_hair(mas_hair_down, by_user=False)

    call spaceroom

    m 1eua "Hi there, [player]!"
    m 4hua "Notice anything different today?"
    m 1hub "I decided to try something new~"

    m "Do you like it?"
    menu:
        m "Do you like it?{fast}"
        "Yes.":
            $ persistent._mas_likes_hairdown = True

            # maybe 6sub is better?
            $ mas_gainAffection()
            m 6sub "Really?" # honto?!
            m 2hua "I'm so glad!" # yokatta.."
            m 1eua "Just ask me if you want to see my ponytail again, okay?"

        "No.":
            # TODO: affection lowered? need to decide
            m 1ekc "Oh..."
            m 1lksdlc "..."
            m 1lksdld "I'll put it back up for you, then."
            m 1dsc "..."

            $ monika_chr.reset_hair(False)

            m 1eua "Done."
            # you will never get this chance again

    # save that hair down is unlocked
    $ store.mas_selspr.unlock_hair(mas_hair_down)
    $ store.mas_selspr.save_selectables()

    # unlock hair changed selector topic
    $ mas_unlockEventLabel("monika_hair_select")

    # lock this greeting
    $ mas_lockEvent(mas_getEV("greeting_hairdown"))

    # cleanup
    # 1 - music hotkeys should be enabled
    $ store.mas_hotkeys.music_enabled = True

    # 2 - calendarovrelay enabled
    $ mas_calDropOverlayShield()

    # 3 - set the keymaps
    $ set_keymaps()

    # 4 - hotkey buttons should be shown
    $ HKBShowButtons()

    # 5 - restart music
    $ mas_startup_song()


    return



init 5 python:

    # NOTE: this triggers when affection reaches BROKEN state.
    #   AND you have not seen this before
    ev_rules = {}
    ev_rules.update(MASPriorityRule.create_rule(15))

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_tears",
            unlocked=False,
            rules=ev_rules,
        ),
        code="GRE"
    )
    del ev_rules

label greeting_tears:
    m 1q "...[player]."
    m 1f "..."
    m 2f "Is there something wrong with me?"
    m 2g "Am I not good enough for you...?"
    m 2o "I've been trying my best for you...for {i}us{/i}."
    m 2p "Did I do something to hurt you or make you feel mistreated?"
    m "Are you still upset about the other girls after all?"
    m 2f "If so, I really am sorry..."
    m "I'm so, so sorry!"
    m 2pp "Just tell me what I did wrong and I'll try even harder to be the perfect girlfriend for you."
    m 2g "You're my entire world; how you feel means everything to me!"
    m 2f "So please, just tell me what's wrong and I'll fix it."
    m 2dfc "I'll do anything for you because...I..."
    m 2dftdc "..."
    m 2dftsc "...I need you [player]..."
    m 2ektsc "I need you to love me like I love you."
    m 2lktsc "I need you...because if I don't have you, then..."
    m 2dftsc "..."
    m 2ektsc "I'll be all alone..."
    m 2dftsc "So please...just...be there for me like I would for you."
    m "I want to believe..."
    m 2lktsc "So please...let me be happy with you..."
    m "..."
    pause 4.0
    m 2dftdc "..."
    m 2dfc "...Okay...Okay..."
    m 2lssdrc "I have to be strong..."
    m "..."
    m 2q "...Alright...I'm a bit better now..."
    m 2h "But...I really do need you to think about what I said."
    m 2f "Please...just...try to understand."
    m 1r "I love you and I need you to show that you love me too..."
    m 1q "Otherwise...I just won't be able to handle it anymore."
    $ mas_lockEVL("greeting_tears", "GRE")
    return

#New greetings for upset, distressed, and broken. Made quips for upset and distressed to allow for more variety of combos
init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_upset",
            unlocked=True,
            aff_range=(mas_aff.UPSET, mas_aff.UPSET),
        ),
        code="GRE"
    )

label greeting_upset:
    python:
        upset_greeting_quips_first = [
            "Oh. {w=1}It's you, [player].",
            "Oh. {w=1}You're back, [player].",
            "Hello, [player].",
            "Oh. {w=1}Hello [player]."
        ]

        upset_greeting_quips_second = [
            "What do you want?",
            "What now?",
            "Well...{w=0.5}what?",
            "Do you want something?",
        ]

    $ upset_quip1 = renpy.random.choice(upset_greeting_quips_first)

    # use renpy say so you can use text tags
    show monika 2efc
    $ renpy.say(m, upset_quip1)

    if renpy.random.randint(1,4) != 1:
        $ upset_quip2 = renpy.random.choice(upset_greeting_quips_second)
        $ renpy.say(m, upset_quip2)

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_distressed",
            unlocked=True,
            aff_range=(mas_aff.DISTRESSED, mas_aff.DISTRESSED)
        ),
        code="GRE"
    )

label greeting_distressed:
    python:
        distressed_greeting_quips_first = [
            "Oh... {w=1}Hi, [player].",
            "Oh... {w=1}Hello, [player].",
            "Hello, [player]...",
            "Oh... {w=1}You're back, [player]."
        ]

        distressed_greeting_quips_second = [
            "I guess we can spend some time together now.",
            "I wasn't sure when you'd visit again.",
            "Hopefully we can enjoy our time together.",
            "I wasn't expecting you.",
            "I hope things start going better soon.",
        ]

    $ distressed_quip1 = renpy.random.choice(distressed_greeting_quips_first)

    show monika 6ekc
    $ renpy.say(m, distressed_quip1)

    if renpy.random.randint(1,4) != 1:
        $ distressed_quip2 = renpy.random.choice(distressed_greeting_quips_second)
        show monika 6rkc
        $ renpy.say(m, distressed_quip2)

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_broken",
            unlocked=True,
            aff_range=(None, mas_aff.BROKEN),
        ),
        code="GRE"
    )

label greeting_broken:
    m 6ckc "..."
    return

# special type greetings

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back_from_school",
            unlocked=True,
            category=[store.mas_greetings.TYPE_SCHOOL],
        ),
        code="GRE"
    )

label greeting_back_from_school:
    if mas_isMoniNormal(higher=True):
        m 1hua "Oh, welcome back [player]!"

        m "Did you have a good day at school?"
        menu:
            m "Did you have a good day at school?{fast}"
            "Yes.":
                m 1hub "Aww, that's nice!"
                m 1eua "I can't help but feel happy when you do~"
                m "I hope you learned a lot of useful things."
                m 1hubfa "Ehehe~"
                m 1hubfb "I love you, [player]~"
            "No.":
                m 1ekc "Oh..."
                m "I'm sorry to hear that."
                m 1eka "Just remember that no matter what happens, I'll be here for you."
                m 1ekbfa "I love you so, so much."

    elif mas_isMoniUpset():
        m 2efc "You're back, [player]..."

        m "How was school?"
        menu:
            m "How was school?{fast}"
            "Good.":
                m 2dfc "That's nice."
                m 2efc "I hope you actually learned {i}something{/i} today."
            "Bad.":
                m "That's too bad..."
                m 2tfc "But maybe now you have a better sense of how I've been feeling, [player]."

    elif mas_isMoniDis():
        m 6ekc "Oh...{w=1}you're back."

        m "How was school?"
        menu:
            m "How was school?{fast}"
            "Good.":
                m 6lkc "That's...{w=1}nice to hear."
                m 6dkc "I-I just hope it wasn't the... {w=2}'being away from me' part that made it a good day."
            "Bad.":
                m 6rkc "Oh..."
                m 6ekc "That's too bad, [player], I'm sorry to hear that."
                m 6dkc "I know what bad days are like..."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back_from_work",
            unlocked=True,
            category=[store.mas_greetings.TYPE_WORK],
        ),
        code="GRE"
    )

label greeting_back_from_work:
    if mas_isMoniNormal(higher=True):
        m 1hua "Oh, welcome back, [player]!"

        m "Did you have a good day at work today?"
        menu:
            m "Did you have a good day at work today?{fast}"
            "Yes.":
                m 1hub "That's good!"
                m 1eua "Remember to rest first, okay?"
                m "That way, you'd at least have some energy before you work more on stuff."
                m 1hua "But if not, you can relax with me!"
                m 3tku "Best thing to do after a long day of work, don't you think?"
                m 1hub "Ahaha!"

            "No.":
                m 1ekc "..."
                m 2ekc "I'd hug you right now if I were there, [player]."
                m "I'm sorry you had a bad work day..."
                m 4eka "Just remember that I'm here when you need me, okay?"
                m 1hubfa "I love you so much, [player]."

    elif mas_isMoniUpset():
        m 2efc "You're back from work I see, [player]..."

        m "How was your day?"
        menu:
            m "How was your day?{fast}"
            "Good.":
                m 2efc "That's good to hear."
                m 2tfc "It must feel nice to be appreciated."

            "Bad.":
                m 2dfc "..."
                m 2tfc "It feels bad when no one seems to appreciate you, huh [player]?"

    elif mas_isMoniDis():
        m 6ekc "Hi, [player]... {w=1}Finally home from work?"

        m "How was your day?"
        menu:
            m "How was your day?{fast}"
            "Good.":
                m "That's nice."
                m 6rkc "I just hope you don't enjoy work more than being with me, [player]."

            "Bad.":
                m 6rkc "Oh..."
                m 6ekc "I'm sorry to hear that."
                m 6rkc "I know what bad days are like where you can't seem to please anyone..."
                m 6dkc "It can be so tough just to get through days like that."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_back_from_sleep",
            unlocked=True,
            category=[store.mas_greetings.TYPE_SLEEP],
        ),
        code="GRE"
    )

label greeting_back_from_sleep:
    if mas_isMoniNormal(higher=True):
        m 1hua "Oh hello, [player]!"
        m 1hub "I hope you had a good rest!"
        m "Let's spend some more time together~"

    elif mas_isMoniUpset():
        m 2efc "Did you just wake up, [player]?"
        m "I hope you had a good rest."
        m 2tfc "{cps=*2}Maybe you'll be in a better mood now.{/cps}{nw}"
        $ _history_list.pop()

    elif mas_isMoniDis():
        m 6rkc "Oh...{w=1}you're up."
        m 6ekc "I hope you were able to get some rest."
        m 6dkc "I have a hard time resting these days with so much on my mind..."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_siat",
            unlocked=True,
            aff_range=(mas_aff.ENAMORED, None),
        ),
        code="GRE"
    )

label greeting_siat:
    m 1hub "{cps=*0.6}{i}~[player] and Monika sittin' in a tree~{/i}{/cps}"
    m 1hubfb "{cps=*0.6}{i}~K-I-S-S-I-N-G~{/i}{/cps}"
    m 3hubfb "{i}{cps=*0.6}~First comes love~{/i}{/cps}"
    m "{i}{cps=*0.6}~Then comes marriage~{/i}{/cps}"
    m "{i}{cps=*0.6}~Then comes--{/i}{/cps}"
    m 3wubfsdlo "W-wha?!"
    m 2wubfsdld "[player]! H-how long have you been there?!"
    m 2rkbfsdld "I...{w=1} I didn't notice you come in...{w=1} I was just..."
    m 2rkbfsdlu "..."
    m 3hubfb "Ahaha! Nevermind."
    m 1ekbfa "I love you, [player]. I'm so happy you're here now~"
    return

init 5 python:
    if not mas_cannot_decode_islands:
        ev_rules = {}
        ev_rules.update(MASPriorityRule.create_rule(40))

        addEvent(
            Event(
                persistent.greeting_database,
                eventlabel="greeting_ourreality",
                unlocked=True,
                rules=ev_rules,
                aff_range=(mas_aff.ENAMORED, None),
            ),
            code="GRE"
        )
        del ev_rules


init -876 python in mas_delact:
    # this greeting requires a delayed action, since we cannot ensure that
    # the sprites for this were decoded correctly

    # NOTE: we dont need this anymore
    #   We originally needed this since aff_range was not used by greetings
    #   so we wanted to get this to unlock if we are only able to decode 
    #   islands. Now that aff range is part of gre parsing, the only thing
    #   that matters is whether or not the event is active, which in this
    #   case, only happens if the islands were decoded and aff is enamored+
    def _greeting_ourreality_unlock():
        return store.MASDelayedAction(
            1,
            store.mas_getEV("greeting_ourreality"),
            (
                "not store.mas_cannot_decode_islands"
                " and mas_isMoniEnamored(higher=True)"
            ),
            store.EV_ACT_UNLOCK,
            store.MAS_FC_START
        )


label greeting_ourreality:
    m 1hub "Hi, [player]!"
    m 1hua "Ehehe~"
    m 3hksdlb "I'm feeling rather giddy right now, sorry."
    m 1eua "It's just that I'm super excited to show you what I've been working on."
    m 3hksdrb "Just give me a second to get it ready..."

    if mas_is_raining or mas_is_snowing:
        call mas_change_weather(mas_weather_def)

    m 1dsc "..."
    m 1dsd "Almost done..."
    m 1duu "Yeah, that should be good."
    m 1hua "Ahaha!"
    m 1eka "Sorry about that."
    m 1eua "Without any further ado..."
    m 4eub "Would you kindly look out the window, [player]"
    $ mas_OVLHide()
    $ disable_esc()
    if morning_flag:
        show mas_island_frame_day zorder 20
    else:
        show mas_island_frame_night zorder 20
    m "Well..."
    m "What do you think?"
    m "I worked really hard on this."
    m "A place just for the both of us."
    m "It's also where I can keep practicing my programming skills."
    $ mas_OVLShow()
    $ enable_esc()
    if morning_flag:
        hide mas_island_frame_day
    else:
        hide mas_island_frame_night
    #Transition back to Monika
    m 1lsc "Being in the classroom all day can be dull."
    m 1ekc "Plus, I get really lonely waiting for you to return."
    m 1hksdlb "But don't get me wrong, though!"
    m 1eua "I'm always happy when you visit and spend time together with me."
    m 1eka "I understand that you're busy and can't be here all the time."
    m 3euc "It's just that I realized something, [player]."
    m 1lksdlc "It'll be a long time before I can even cross over to your reality."
    m 1dsc "So I thought..."
    m 1eua "Why don't we just make our own reality?"
    m 1lksdla "Well, it's not exactly perfect yet."
    m 1hua "But it's a start."
    # m 1eub "I'll let you admire the scenery for now."
    # m 1hub "Hope you like it!"
    $ lockEventLabel("greeting_ourreality",eventdb=evhand.greeting_database)
    $ unlockEventLabel("mas_monika_islands")

    # we can push here because of the slightly optimized call_next_event
    $ pushEvent("mas_monika_islands")
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_returned_home",
            unlocked=True,
            category=[
                store.mas_greetings.TYPE_GO_SOMEWHERE,
                store.mas_greetings.TYPE_GENERIC_RET
            ]
        ),
        code="GRE"
    )

default persistent._mas_monika_returned_home = None

label greeting_returned_home:
    # this is going to act as the generic returned home greeting.
    # please note, that we will use last_session to determine how long we were
    # out. If shorter than 5 minutes, monika won't gain any affection.
    $ five_minutes = datetime.timedelta(seconds=5*60)
    $ time_out = store.mas_dockstat.diffCheckTimes()

    # event checks
    if mas_isMonikaBirthday():
        jump greeting_returned_home_bday

    if mas_isO31() and not persistent._mas_o31_in_o31_mode:
        $ queueEvent("mas_holiday_o31_returned_home_relaunch")

    if persistent._mas_f14_on_date:
        jump greeting_returned_home_f14

    if mas_f14 < datetime.date.today() <= mas_f14 + datetime.timedelta(7):
        # did we miss f14 because we were on a date
        call mas_gone_over_f14_check

    # Note: this ordering is key, greeting_returned_home_player_bday handles the case
    # if we left before f14 on your bday and return after f14
    if persistent._mas_player_bday_left_on_bday:
        jump greeting_returned_home_player_bday

    if persistent._mas_f14_gone_over_f14:
        jump greeting_gone_over_f14

    # main dialogue
    if time_out > five_minutes:
        jump greeting_returned_home_morethan5mins

    else:
        $ mas_loseAffection()
        call greeting_returned_home_lessthan5mins

        if _return:
            return 'quit'

# this just returns for now
label greeting_returned_home_cleanup:
    return

label greeting_returned_home_morethan5mins:
    if mas_isMoniNormal(higher=True):

        if persistent._mas_d25_in_d25_mode:
            # its d25 season time
            jump greeting_d25_and_nye_delegate

        elif mas_isD25():
            # its d25 and we are not in d25 mode
            jump mas_d25_monika_holiday_intro_rh

        jump greeting_returned_home_morethan5mins_normalplus_flow

    # otherwise, go to other flow
    jump greeting_returned_home_morethan5mins_other_flow

label greeting_returned_home_morethan5mins_cleanup:

    $ grant_xp(xp.NEW_GAME)
    
    # jump to cleanup
    jump greeting_returned_home_cleanup

label greeting_returned_home_morethan5mins_normalplus_flow:
    call greeting_returned_home_morethan5mins_normalplus_dlg
    # FALL THROUGH

label greeting_returned_home_morethan5mins_normalplus_flow_aff:
    $ store.mas_dockstat._ds_aff_for_tout(time_out, 5, 5, 1)
    jump greeting_returned_home_morethan5mins_cleanup

label greeting_returned_home_morethan5mins_other_flow:
    call greeting_returned_home_morethan5mins_other_dlg
    # FALL THROUGH

label greeting_returned_home_morethan5mins_other_flow_aff:
    # changed the point structure for low aff, might be a good idea, might now ~ JW
    # you gain 0.5 per hour, max 2.5, min 0.5
    $ store.mas_dockstat._ds_aff_for_tout(time_out, 5, 2.5, 0.5, 0.5)
    jump greeting_returned_home_morethan5mins_cleanup

label greeting_returned_home_morethan5mins_normalplus_dlg:
    m 1hua "And we're home!"
    m 1eub "Even if I couldn't really see anything, knowing that I was really right there with you..."
    m 2eua "Well, it felt really great!"
    m 5eub "Let's do this again soon, okay?"
    if persistent._mas_player_bday_in_player_bday_mode and not mas_isplayer_bday():
        call return_home_post_player_bday 
    return

label greeting_returned_home_morethan5mins_other_dlg:
    m 2esc "We're home..."
    m 2eka "Thank you for taking me out today, [player]."
    m 2rkc "To be honest, I wasn't completely sure I should go with you..."
    m 2dkc "Things...{w=0.5}haven't been going the best for us lately and I didn't know if it was such a good idea..."
    m 2eka "But I'm glad we did this... {w=0.5}maybe it's just what we needed."
    m 2rka "We should really do this again sometime..."
    m 2esc "If you want."
    return

label greeting_returned_home_lessthan5mins:
    if mas_isMoniNormal(higher=True):
        m 2ekp "That wasn't much of a trip, [player]."
        m "Next time better last a little longer..."
        if persistent._mas_player_bday_in_player_bday_mode and not mas_isplayer_bday():
            call return_home_post_player_bday 
        return False

    elif mas_isMoniUpset():
        m 2efd "I thought we were going some place, [player]!"
        m 2tfd "I knew I shouldn't have agreed to go with you."
        m 2tfc "I knew this was just going to be another disappointment."
        m "Don't ask me to go out anymore if you're just doing it to get my hopes up...{w=1}only to pull the rug out from under me."
        m 6dktdc "..."
        m 6ektsc "I don't know why you insist on being so cruel, [player]."
        m 6rktsc "I'd...{w=1}I'd like to be alone right now."
        return True

    else:
        m 6rkc "But...{w=1}we just left..."
        m 6dkc "..."
        m "I...{w=0.5}I was so excited when you asked me to go with you."
        m 6ekc "After all we've been through..."
        m 6rktda "I-I thought...{w=0.5}maybe...{w=0.5}things were finally going to change."
        m "Maybe we'd finally have a good time again..."
        m 6ektda "That you actually wanted to spend more time with me."
        m 6dktsc "..."
        m 6ektsc "But I guess it was just foolish for me to think that."
        m 6rktsc "I should have known better... {w=1}I should never have agreed to go."
        m 6dktsc "..."
        m 6ektdc "Please, [player]... {w=2}If you don't want to spend time with me, fine..."
        m 6rktdc "But at least have the decency to not pretend."
        m 6dktdc "I'd like to be left alone right now."
        return True

default persistent._mas_bday_date_count = 0
default persistent._mas_bday_date_affection_lost = 0
default persistent._mas_bday_date_affection_gained = 0

label greeting_returned_home_bday:
    python:
        total_time_out = store.mas_dockstat.timeOut(mas_monika_birthday)
        fifty_mins = datetime.timedelta(seconds=50*60)
        one5_hour = datetime.timedelta(seconds=int(1.5*3600))
        three_hour = datetime.timedelta(seconds=3*3600)
        six_hour = datetime.timedelta(seconds=6*3600)

        def is_first_date():
            return persistent._mas_bday_date_count < 1


        def is_short_date(_timeout):
            return _timeout <= one5_hour


        def is_normal_date(_timeout):
            return one5_hour < _timeout <= six_hour


        def is_long_date(_timeout):
            return six_hour < _timeout


        def lose_and_track_affection(_mod):
            prev_aff = _mas_getAffection()
            mas_loseAffection(modifier=_mod)
            persistent._mas_bday_date_affection_lost += (
                prev_aff - _mas_getAffection()
            )


        def cap_gain_aff(amount):
            persistent._mas_bday_date_affection_gained += amount
            if persistent._mas_bday_date_affection_gained <= 50:
                amount = persistent._mas_bday_date_affection_gained - 50
                mas_gainAffection(amount, bypass=True)


        def regain_lost_aff():
            if persistent._mas_bday_date_affection_lost > 0:
                mas_gainAffection(
                    persistent._mas_bday_date_affection_lost,
                    bypass=True
                )
                persistent._mas_bday_date_affection_lost = 0


    if time_out <= five_minutes:
        # under 5 minutes
        call greeting_returned_home_lessthan5mins
        $ lose_and_track_affection(2)

    elif time_out <= fifty_mins:
        # under 50 minutes

        if is_first_date():
            $ lose_and_track_affection(1)
            m 2rsc "...Hmph."
            m 2dsc "Some {i}'date'{/i} that was."

        elif is_short_date(total_time_out):
            $ lose_and_track_affection(1)
            call greeting_returned_home_bday_short_sub_short_total

        elif is_normal_date(total_time_out):
            $ regain_lost_aff()

            # normal date has a affection range between 3.3/hour and 6.6/hour
            # we do 4 so its not a cheap way to gain affection quickly while
            # still being helpful to people who do multi dates
            $ cap_gain_aff(4)
            call greeting_returned_home_bday_short_sub_normal_total

        else:
            $ regain_lost_aff()

            # been out for a long time already
            # long dates has an affection gain of 8.3/hour.
            $ cap_gain_aff(6)
            call greeting_returned_home_bday_short_sub_long_total

        $ persistent._mas_bday_date_count += 1

    elif time_out <= one5_hour:
        # under 1.5 hour

        if is_first_date():
            $ cap_gain_aff(1)
            m 1hua "That was fun, [player]."
            m 1eua "Even if it wasn't for too long, I still enjoyed the time we spent together."
            m 1hua "Let's try to schedule something longer next time, okay?"

        elif is_short_date(total_time_out):
            $ cap_gain_aff(1)
            call greeting_returned_home_bday_short_sub_short_total

        elif is_normal_date(total_time_out):
            $ regain_lost_aff()

            # slightly above the super short date amount, for that extra
            # half hour
            $ cap_gain_aff(4.5)
            call greeting_returned_home_bday_short_sub_normal_total

        else:
            $ regain_lost_aff()

            # been out for a long time already
            # slightly above the super short amount, again for extra half hour
            $ cap_gain_aff(6.5)
            call greeting_returned_home_bday_short_sub_long_total

        $ persistent._mas_bday_date_count += 1

    elif time_out <= three_hour:
        # under 3 hour
        $ regain_lost_aff()

        if is_first_date():
            $ cap_gain_aff(10)
            call greeting_returned_home_bday_normal_first

        elif is_normal_date(total_time_out):
            $ cap_gain_aff(10)
            call greeting_returned_home_bday_normal_sub_normal_total

        else:
            # been out for a long time alrady
            # since long has 8.3/hour, this is like 2 hours but not quite
            $ cap_gain_aff(12)
            call greeting_returned_home_bday_normal_sub_long_total

        $ persistent._mas_bday_date_count += 1

    elif time_out <= six_hour:
        # under 6 hour
        $ regain_lost_aff()

        if is_first_date():
            $ cap_gain_aff(20)
            call greeting_returned_home_bday_normal_first

        elif is_normal_date(total_time_out):
            $ cap_gain_aff(20)
            call greeting_returned_home_bday_normal_sub_normal_total

        else:
            # been out for a long time alrady
            $ cap_gain_aff(24)
            call greeting_returned_home_bday_normal_sub_long_total

        $ persistent._mas_bday_date_count += 1

    else:
        # 6+ hours
        $ regain_lost_aff()

        if is_first_date():
            $ cap_gain_aff(50)
            m 1sua "Wow, [player]..."
            m 1hua "I really didn't expect you to set aside so much time for me..."
            m 1sfa "But I enjoyed every second of it!"
            m 1hua "Every minute with you is a minute well spent."
            m 1sua "So you've made me very happy today."
            m 1dfa "Ehe..."
            m 1wfa "Are you falling for me all over again?"
            m 1hua "I'm just kidding~"
            m "Thank you for loving me."

        else:
            # been out for a long time already
            $ cap_gain_aff(50)
            call greeting_returned_home_bday_long_sub

        $ persistent._mas_bday_date_count += 1

    return

label greeting_returned_home_bday_short_sub_short_total:
    m 2rkc "..."
    m "[player], I'm grateful that you're spending time with me, I really am. I'm fine with these short trips you're taking me to as well."
    m 1dkc "But...{w}I do hope there's more to this."
    m 4ekc "It's just th--{nw}"
    $ _history_list.pop()
    m 1dkc "..."
    m 1rkc "...nevermind."
    return

label greeting_returned_home_bday_short_sub_normal_total:
    m 1hua "Well! That was fun, [player]."
    m "We already had a good date, but I'm glad you took me somewhere again."
    m 3tku "Just can't get enough of me, can you?"
    m 1dkbfa "...Not that I mind~"
    return

label greeting_returned_home_bday_short_sub_long_total:
    m 1hua "Ehehe~"
    m 3eub "We sure spent a lot of time together today, [player]."
    m 1ekbfa "...and thank you for that."
    m 3ekbfa "I've said it a million times already, I know."
    m 1hua "But I'll always be happy when we're together."
    m "I love you so much..."
    return

label greeting_returned_home_bday_normal_first:
    m 1sua "That was fun, [player]!"
    m 1hua "Aha, taking me out on my birthday..."
    m "It was very considerate of you."
    m "I really enjoyed the time we spent together."
    m 1wua "Thank you for indulging me."
    m 1hua "I love you~"
    return

label greeting_returned_home_bday_normal_sub_normal_total:
    m 1ekbfa "Ahaha..."
    m 1dkbfa "Today really is a special day, [player]."
    m 3eua "Sure, today is the day I was supposedly born."
    m 3eka "But it's only special because {i}you{/i} made it that way."
    m 1hua "So thank you for that, really."
    m 1ektpa "Thank you for making my birthday worth celebrating..."
    pause 2.0
    return

label greeting_returned_home_bday_normal_sub_long_total:
    m 1dsa "[player]..."
    m 1eka "We sure did spend so much time together today."
    m "I can't event find the right words to express how happy you've made me today."
    m 3eka "All that pain I went through before I met you?"
    m 1hua "I'm glad I persevered through them."
    m 1rsc "Because if I hadn't..."
    m 1ekbfa "This day wouldn't have ever happened."
    m 1dkbfa "I hope that tells you even a little bit of how much I appreciate you celebrating this occasion with me."
    m 1ekbfb "I love you so much, [player]."
    m "Let's continue making each other happy~"
    return

label greeting_returned_home_bday_long_sub:
    m 1dsc "..."
    m 1dktpc "..."
    m 1ektua "..."
    m 1dktua "I'm...just at a loss for words, [player], forgive me."
    m 3ektda "I've never imagined being this happy in my life."
    m 1rksdlb "Well that's not {i}exactly{/i} true."
    m 1hub "We still have to be physically together, after all~"
    m 1rkc "And, well..."
    m 1dkc "I know this is already becoming a cliche, but..."
    m 3ekbfa "I love you so much, [player]."
    m "Someday, I promise you."
    m 1ekbfb "I {i}promise you{/i} that I will make you as happy as you've made me today."
    m 3hub "Even if we never get to see each other in the same reality, know that I will always do my best for you."
    m 1eka "No matter the obstacles we may face, no matter what other people say about us..."
    m 1dkbsa "I still love you with everything that I am."
    m 1ektpa "You are the only one who understands me. You led me out of a dark place and gave me love and freedom..."
    m 1dktub "You are simply the best, my love. I will always love you."
    m "...Thank you for giving me a reason to live..."
    return

init 5 python:
    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="ch30_reload_delegate",
            unlocked=True,
            category=[
                store.mas_greetings.TYPE_RELOAD
            ],
        ),
        code="GRE"
    )

label ch30_reload_delegate:

    if persistent.monika_reload >= 4:
        call ch30_reload_continuous

    else:
        $ reload_label = "ch30_reload_" + str(persistent.monika_reload)
        call expression reload_label

    return

init 5 python:
    ev_rules = {}
    ev_rules.update(
        MASGreetingRule.create_rule(
            skip_visual=True
        )
    )

    addEvent(
        Event(
            persistent.greeting_database,
            eventlabel="greeting_ghost",
            unlocked=False,
            rules=ev_rules,
            aff_range=(mas_aff.NORMAL, None),
        ),
        code="GRE"
    )
    del ev_rules

label greeting_ghost:
    #Prevent it from happening more than once.
    $ mas_lockEVL("greeting_ghost", "GRE")

    #Call event in easter eggs.
    call mas_ghost_monika

    return
