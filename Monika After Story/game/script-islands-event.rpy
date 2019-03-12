# Monika's ???? Event
# deserves it's own file because of how much dialogue these have
# it basically shows a new screen over everything, and has an image map
# Monika reacts to he place the player clicks

### initialize the island images
init -10 python:
    ## NOTE: we assume 2 things:
    #   - we have write access to teh mod_assets folder
    #   - the existing pngs dont exist yet
    #
    #   if for some reason we fail to convert the files into images
    #   then we must backout of showing the event.
    # 
    #   NOTE: other things to note:
    #       on o31, we cannot have islands event
    mas_cannot_decode_islands = not store.mas_island_event.decodeImages()


init -11 python in mas_island_event:
    import store
    import store.mas_dockstat as mds
    import store.mas_ics as mis

    # setup the docking station we are going to use here
    islands_station = store.MASDockingStation(mis.islands_folder)

    def decodeImages():
        """
        Attempts to decode the iamges

        Returns TRUE upon success, False otherwise
        """
        return mds.decodeImages(islands_station, mis.islands_map)


    def removeImages():
        """
        Removes the decoded images at the end of their lifecycle

        AKA quitting
        """
        mds.removeImages(islands_station, mis.islands_map)


init 4 python:
    # adjustments to islands flags in the case of other runtime things
    if mas_isO31():
        # no islands event on o31
        mas_cannot_decode_islands = True
        store.mas_island_event.removeImages()


init 5 python:
    if not mas_cannot_decode_islands:
        addEvent(
            Event(
                persistent.event_database,
                eventlabel="mas_monika_islands",
                category=['monika','misc'],
                prompt="Can you show me the floating islands?",
                pool=True,
                unlocked=False,
                rules={"no unlock": None},
                aff_range=(mas_aff.ENAMORED, None)
            )
        )

init -876 python in mas_delact:
    # this event requires a delayed aciton, since we cannot ensure that
    # the sprites for this were decoded correctly

    def _mas_monika_islands_unlock():
        return store.MASDelayedAction.makeWithLabel(
            2,
            "mas_monika_islands",
            (
                "not store.mas_cannot_decode_islands"
                " and mas_isMoniEnamored(higher=True)"
            ),
            store.EV_ACT_UNLOCK,
            store.MAS_FC_START
        )


label mas_monika_islands:
    m 1eub "I'll let you admire the scenery for now."
    m 1hub "Hope you like it!"

    # prevent interactions
    $ mas_RaiseShield_core()
    $ mas_OVLHide()
    $ disable_esc()
    $ renpy.store.mas_hotkeys.no_window_hiding = True

    # keep looping the screen
    $ _mas_island_keep_going = True

    # keep track about the window
    $ _mas_island_window_open = True

    # text used for the window
    $ _mas_toggle_frame_text = "Close Window"

    # shimeji flag
    $ _mas_island_shimeji = False

    # random chance to get mini moni appear
    if renpy.random.randint(1,100) == 1:
        $ _mas_island_shimeji = True

    # double screen trick
    show screen mas_islands_background

    # keep showing the event until the player wants to go
    while _mas_island_keep_going:

        # image map with the event
        call screen mas_show_islands()

        if _return:
            # call label if we have one
            call expression _return
        else:
            # player wants to quit the event
            $ _mas_island_keep_going = False
    # hide extra screen
    hide screen mas_islands_background

    # drop shields
    $ mas_DropShield_core()
    $ mas_OVLShow()
    $ enable_esc()
    $ store.mas_hotkeys.no_window_hiding = False

    m 1eua "I hope you liked it, [player]~"
    return

label mas_monika_upsidedownisland:
    m "Oh, that."
    m "I guess you're wondering why that island is upside down, right?"
    m "Well...I was about to fix it until I took another good look at it."
    m "It looks surreal, doesn't it?"
    m "I just feel like there's something special about it."
    m "It's just… mesmerizing."
    return

label mas_monika_glitchedmess:
    m "Oh, that."
    m "It's something I'm currently working on."
    m "It's still a huge mess, though. I'm still trying to figure out how to be good at it."
    m "In due time, I'm sure I'll get better at coding!"
    m "Practice makes perfect after all, right?"
    return

label mas_monika_cherry_blossom_tree:
    python:

        if not renpy.store.seen_event("mas_monika_cherry_blossom1"):

            renpy.call("mas_monika_cherry_blossom1")

        else:
            _mas_cherry_blossom_events = ["mas_monika_cherry_blossom1",
                "mas_monika_cherry_blossom2", "mas_monika_cherry_blossom3",
                "mas_monika_cherry_blossom4"]

            renpy.call(renpy.random.choice(_mas_cherry_blossom_events))

    return

label mas_monika_cherry_blossom1:
    m "It's a beautiful tree, isn't it?"
    m "It's called a Cherry Blossom tree."
    m "They're native to Japan."
    m "Traditionally, when the flowers are in bloom, people would go flower viewing and have a picknick underneath the trees."
    m "Well, I didn't choose this tree because of tradition."
    m "I chose it because it's lovely and pleasing to look at."
    m "Just staring at the falling petals is just awe-inspiring."
    return

label mas_monika_cherry_blossom2:
    m "Did you know you can eat the flower petals of a  Cherry Blossom tree?"
    m "I don't know the taste myself, but I'm sure it'd be as sweet as you."
    m "Ehehe~"
    return

label mas_monika_cherry_blossom3:
    m "You know, the tree is symbolic like life itself."
    m "Beautiful, but shortlived."
    m "But with you here, it's always blooming beautifully."
    m "Know that I'll always be grateful to you for being in my life."
    m "I love you, [player]~"
    return

label mas_monika_cherry_blossom4:
    m "You know what'd be nice to drink under the Cherry Blossom tree?"
    m "A little sake~"
    m "Ahaha! I'm just kidding"
    m "I'd rather have tea or coffee."
    m "But, it'd be nice to watch the falling petals with you."
    m "That'd be really romantic~"
    return

label mas_monika_sky:
    python:

        if morning_flag:
            _mas_sky_events = ["mas_monika_day1","mas_monika_day2",
                "mas_monika_day3"]

        else:
            _mas_sky_events = ["mas_monika_night1","mas_monika_night2",
                "mas_monika_night3"]

        _mas_sky_events.append("mas_monika_daynight1")
        _mas_sky_events.append("mas_monika_daynight2")

        renpy.call(renpy.random.choice(_mas_sky_events))

    return

label mas_monika_day1:
    m "It's a nice day today."
    m "This weather would be good for a little book reading under the Cherry Blossom tree right, [player]?"
    m "Lying under the shade while reading my favorite book."
    m "Along with a snack and your favorite drink on the side."
    m "Ahh, that'd be really nice to do~"
    return

label mas_monika_day2:
    m "The weather looks nice."
    m "This would definitely be the best time to have a picnic."
    m "We even have a great view to accompany it with!"
    m "Wouldn't it be nice?"
    m "Eating under the Cherry Blossom tree."
    m "Adoring the scenery around us."
    m "Enjoying ourselves with each other's company."
    m "Ahh, that'd be fantastic~"
    return

label mas_monika_day3:
    m "It's pretty peaceful outside."
    m "I wouldn't mind lazing around the grass right now."
    m "Or your head resting on my lap..."
    m "Ah!"
    m "Uh..."
    m "Ahaha!"
    m "N-nevermind!"
    m "Just forget what I said..."
    return

label mas_monika_night1:
    m "You're probably wondering what happened to that orange comet that occassionaly passes by."
    m "Don't worry, I've dealt with it."
    m "I wouldn't want you to get hurt~"
    return

label mas_monika_night2:
    m "Have you ever gone stargazing, [player]?"
    m "Taking some time out of your evening to look at the night sky and to just stare at the beauty of the sky above..."
    m "It's surprisingly relaxing, you know?"
    m "I've found that it can really relieve stress and clear your head..."
    m "And seeing all kinds of constellations in the sky just fills your mind with wonder."
    m "Of course, it really makes you realize just how small we are in the universe."
    m "Ahaha..."
    return

label mas_monika_night3:
    m "What a beautiful night!"
    m "If I could, I'd add fireflies."
    m "Their lights complement the night sky, it's a pretty sight."
    m "Improve the ambience a little, you know?"
    return

label mas_monika_daynight1:
    m "Maybe I should add more shrubs and trees."
    m "Make the islands prettier you know?"
    m "I just have to find the right flowers and foliage to go with it."
    m "Or maybe each island should have its own set of plants so that everything will be different and have variety."
    m "I'm getting excited thinking about it~"
    return

label mas_monika_daynight2:
    # aurora borealis
    m "{i}Windmill, windmill for the land{/i}"

    # a-aurora borealis
    m "{i}Turn forever hand in hand{/i}"

    # aurora borealis
    m "{i}Take it all in on your stride{/i}"

    # at this time of day?
    m "{i}It is ticking, falling down{/i}"

    # aurora borealis
    m "{i}Love forever, love has freely{/i}"

    # a-aurora borealis
    m "{i}Turned forever you and me{/i}"

    # in this part of the country? Yes
    m "{i}Windmill, windmill for the land{/i}"

    m "Ehehe, don't mind me, I just wanted to sing out of the blue~"
    return

label mas_island_shimeji:
    m "Ah!"
    m "How'd she get there?"
    m "Give me a second, [player]..."
    $ _mas_island_shimeji = False
    m "All done!"
    m "Don't worry, I just moved her to a different place."
    return

label mas_island_bookshelf:
    python:

        _mas_bookshelf_events = ["mas_island_bookshelf1",
                "mas_island_bookshelf2"]

        renpy.call(renpy.random.choice(_mas_bookshelf_events))

    return

label mas_island_bookshelf1:
    m "Some of my favorite books are in there."
    m "{i}Fahrenheit 451{/i}, {i}Hard-Boiled Wonderland{/i}, {i}Nineteen Eighty-Four{/i} and a few others."
    m "Maybe we can read them together sometime~"
    return

label mas_island_bookshelf2:
    m "Reading outdoors is a nice change of pace, you know?"
    m "I'd take a cool breeze over a stuffy library any day."
    m "Maybe I should add a table underneath the Cherry Blossom tree."
    m "It'd be nice to enjoy a cup of coffee with some snacks to go alongside my book reading."
    m "That'd be wonderful~"
    return

screen mas_islands_background:

    # NOTE: we will ALWAYS show the islands firs time without any weather options
    add mas_current_weather.isbg_window(morning_flag, _mas_island_window_open)

#    if morning_flag:
#        if _mas_island_window_open:
#            add "mod_assets/location/special/without_frame.png"
#        else:
#            add "mod_assets/location/special/with_frame.png"
#    else:
#        if _mas_island_window_open:
#            add "mod_assets/location/special/night_without_frame.png"
#        else:
#            add "mod_assets/location/special/night_with_frame.png"

    if _mas_island_shimeji:
        add "gui/poemgame/m_sticker_1.png" at moni_sticker_mid:
            xpos 935
            ypos 395
            zoom 0.5

screen mas_show_islands():
    style_prefix "island"
    imagemap:

        ground mas_current_weather.isbg_window(morning_flag, _mas_island_window_open)

#        if mas_is_raining:
#            if _mas_island_window_open:
#                ground "mod_assets/location/special/rain_without_frame.png"
#            else:
#                ground "mod_assets/location/special/rain_with_frame.png"
#        elif morning_flag:
#            if _mas_island_window_open:
#                ground "mod_assets/location/special/without_frame.png"
#            else:
#                ground "mod_assets/location/special/with_frame.png"
#        else:
#            if _mas_island_window_open:
#                ground "mod_assets/location/special/night_without_frame.png"
#            else:
#                ground "mod_assets/location/special/night_with_frame.png"


        hotspot (11, 13, 314, 270) action Return("mas_monika_upsidedownisland") # island upside down
        hotspot (403, 7, 868, 158) action Return("mas_monika_sky") # sky
        hotspot (699, 347, 170, 163) action Return("mas_monika_glitchedmess") # glitched house
        hotspot (622, 269, 360, 78) action Return("mas_monika_cherry_blossom_tree") # cherry blossom tree
        hotspot (716, 164, 205, 105) action Return("mas_monika_cherry_blossom_tree") # cherry blossom tree
        hotspot (872, 444, 50, 30) action Return("mas_island_bookshelf") # bookshelf

        if _mas_island_shimeji:
            hotspot (935, 395, 30, 80) action Return("mas_island_shimeji") # Mini Moni

    if _mas_island_shimeji:
        add "gui/poemgame/m_sticker_1.png" at moni_sticker_mid:
            xpos 935
            ypos 395
            zoom 0.5

    hbox:
        yalign 0.98
        xalign 0.96
        textbutton _mas_toggle_frame_text action [ToggleVariable("_mas_island_window_open"),ToggleVariable("_mas_toggle_frame_text","Open Window", "Close Window") ]
        textbutton "Go Back" action Return(False)


# Defining a new style for buttons, because other styles look ugly

# properties for these island view buttons
# copied from hkb
define gui.island_button_height = None
define gui.island_button_width = 205
define gui.island_button_tile = False
define gui.island_button_text_font = gui.default_font
define gui.island_button_text_size = gui.text_size
define gui.island_button_text_xalign = 0.5
define gui.island_button_text_idle_color = "#000"
define gui.island_button_text_hover_color = "#fa9"
define gui.island_button_text_kerning = 0.2

style island_button is button
style island_button_text is button_text

style island_button is default:
    properties gui.button_properties("island_button")
    idle_background  "mod_assets/island_idle_background.png"
    hover_background "mod_assets/island_hover_background.png"
    ypadding 5
    hover_sound gui.hover_sound
    activate_sound gui.activate_sound

style island_button_text is default:
    properties gui.button_text_properties("island_button")
    idle_background  "mod_assets/island_idle_background.png"
    hover_background "mod_assets/island_hover_background.png"
    outlines []

# mini moni ATL
transform moni_sticker_mid:
    block:
        function randomPauseMonika
        parallel:
            sticker_move_n
        repeat
