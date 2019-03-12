# test bday art

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_bday_visuals",
            category=["dev"],
            prompt="BDAY VISUALS",
            pool=True,
            unlocked=True
        )
    )

label dev_bday_visuals:
    m 1eua "hi there, i will now test the birthday visuals"

    m "start with banner"
    show mas_bday_banners zorder 7

    m "now for balloons"
    show mas_bday_balloons zorder 8

    m "now for cake"
    show mas_bday_cake zorder 11

    m "now for lit cake"
    $ mas_bday_cake_lit = True

    m "how does that look?"

    m "okay time to hide"
    hide mas_bday_banners
    hide mas_bday_balloons
    hide mas_bday_cake
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_bday_visual_files",
            category=["dev"],
            prompt="BDAY VISUALS (Files)",
            pool=True,
            unlocked=True
        )
    )

label dev_bday_visual_files:
    m 1eua "Okay, lets try looking for the files we need"
    $ store.mas_dockstat.surpriseBdayShowVisuals()

    m "candle light?"
    $ mas_bday_cake_lit = True

    m "off"
    $ mas_bday_cake_lit = False

    m "remove visuals"
    $ store.mas_dockstat.surpriseBdayHideVisuals()
    m "done"
    return
