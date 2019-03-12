# dev related farewells

init python:
    if persistent._mas_fastbye is None:
        persistent._mas_fastbye = config.developer
        

init 5 python:
    rules = dict()
    rules.update(MASNumericalRepeatRule.create_rule(repeat=EV_NUM_RULE_YEAR))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_st_patrick",
            start_date=datetime.datetime(2017, 3, 17, 5),
            end_date=datetime.datetime(2017, 3, 18, 5),
            unlocked=True,
            rules=rules
        ),
        eventdb=evhand.farewell_database
    )
    del rules

label bye_st_patrick:
    m 1c "Aww, leaving already?"
    m 1e "It's really sad whenever you have to go..."
    m 1b "Good luck with the hangover!"
    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASFarewellRule.create_rule(random_chance=10))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_dev",
            unlocked=True,
            rules=rules
        ),
        eventdb=evhand.farewell_database
    )
    del rules

label bye_dev:
    m 1c "How's the new feature going, eh [player]?"
    m 1e "Or maybe you're just running some tests?"
    m 1k "Don't give up until everything works as expected!"
    return 'quit'

# Dev Fast farewell
init 5 python:
    if persistent._mas_fastbye:
        rules = dict()
        rules.update(MASSelectiveRepeatRule.create_rule(hours=range(0,24)))
        rules.update({"monika wants this first":""})
        addEvent(
            Event(
                persistent.farewell_database,
                eventlabel="bye_fast",
                unlocked=True,
                rules=rules
            ),
            eventdb=evhand.farewell_database
        )
        del rules

label bye_fast:
    m "{fast}Bye!{nw}"
    return 'quit'


# This one exists so devs get an autoupdate once they pull these changes
init 5 python:
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_dev_temp",
            unlocked=True
        ),
        eventdb=evhand.farewell_database
    )

label bye_dev_temp:
    m 1c "Leaving now, eh [player]?"
    m 1e "We had some changes in the farewell system, I need to update something first ..."
    python:
        for k in evhand.farewell_database:
            # no need to do any special checks since all farewells were already available
            renpy.store.evhand.farewell_database[k].unlocked = True
    $ evhand.farewell_database["bye_dev_temp"].unlocked = False
    m 1k "All done, thanks for waiting [player]!"
    #Don't show this farewell again
    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASAffectionRule.create_rule(min=20,max=None))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_dev_love",
            unlocked=True,
            rules=rules
        ),
        eventdb=evhand.farewell_database
    )
    del rules

label bye_dev_love:
    m 1c "Aww, leaving already?"
    m 1e "It's really sad whenever you have to go..."
    m 5a "I love you so much [player]!"
    m 5a "Never forget that!"
    return 'quit'

init 5 python:
    rules = dict()
    rules.update(MASAffectionRule.create_rule(min=None,max=-20))
    addEvent(
        Event(
            persistent.farewell_database,
            eventlabel="bye_dev_no_hate",
            unlocked=True,
            rules=rules
        ),
        eventdb=evhand.farewell_database
    )
    del rules

label bye_dev_no_hate:
    m 1c "Leaving already, huh?"
    m 1e "I hope you finish the testing quick"
    m 1h "I want to feel loved again soon"
    m "Bye"
    return 'quit'
