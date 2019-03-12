# AFF010 is progpoints
#
# Affection module:
#
# General:
#
# This module is aimed to keep track and determine Monika's affection
# towards the player. Said affection level will be used to trigger
# specific events.
#
# Affection mechanics:
#
# - Affection gain has a 7 points cap per day
# - Affection lose doesn't have a cap
# - Max and Min possible values for affection are 1000000 and -1000000 respectively
# - Player lose affection every time it takes longer than 1 week to visit Monika
#     the reduction is measured by the formula number_of_days_absent * 0.5
#     if by doing that reduction affection were to be higher than -101 it will be
#     be set to -101. If absent time were higher than 10 years she'll go to -200
# - Affection is given or lost by specific actions the player can do or decisions
#     the player makes
#
# Affection level determine some "states" in which Monika is. Said states are the
# following:
#
# LOVE (1000 and up)
#   Monika is completely comfortable with the player.
#   (aka the comfortable stage in a relationship)
# ENAMORED (400 up to 999)
#     Exceptionally happy, the happiest she has ever been in her life to that point. Completely trusts the player and wants to make him/her as happy as she is.
# AFFECTIONATE (100 up to 399)
#     Glad that the relationship is working out and has high hopes and at this point has no doubts about whether or not it was worth it.
# HAPPY (030 up to 99)
#     Happy with how it is, could be happier but not sad at all.
# NORMAL (-29 up to 29)
#     Has mild doubts as to whether or not her sacrifices were worth it but trusts the player to treat her right. Isn't strongly happy or sad
# UPSET (-74 up to -30)
#     Feeling emotionally hurt, starting to have doubts about whether or not the player loves her and whether or not she she was right regarding what she did in the game.
# DISTRESSED (-99 up to -75)
#     Convinced the player probably doesn't love her and that she may never escape to our reality.
# BROKEN  (-100 and lower)
#     Believes that not only does the player not love her but that s/he probably hates her too because of she did and is trying to punish her. Scared of being alone in her own reality, as well as for her future.
#############

init python:
    # need to initially define this so it can be used in topic / event creation
    mas_curr_affection = store.mas_affection.NORMAL
    mas_curr_affection_group = store.mas_affection.G_NORMAL

init -900 python in mas_affection:
    # this is very early because they are importnat constants
    
    # numerical constants of affection levels
    BROKEN = 1
    DISTRESSED = 2
    UPSET = 3
    NORMAL = 4
    HAPPY = 5
    AFFECTIONATE = 6
    ENAMORED = 7
    LOVE = 8

    # natural order of affection levels
    _aff_order = [
        BROKEN,
        DISTRESSED,
        UPSET,
        NORMAL,
        HAPPY,
        AFFECTIONATE,
        ENAMORED,
        LOVE
    ]

    # dict map of affection levels. This is purely for O(1) checking
    _aff_level_map = {}
    for _item in _aff_order:
        _aff_level_map[_item] = _item

    # cascade map of affection levels
    # basically, given a level, which is the next level closet to NORMAL
    _aff_cascade_map = {
        BROKEN: DISTRESSED,
        DISTRESSED: UPSET,
        UPSET: NORMAL,
        HAPPY: NORMAL,
        AFFECTIONATE: HAPPY,
        ENAMORED: AFFECTIONATE,
        LOVE: ENAMORED
    }


    # numerical constants of affection groups
    G_SAD = -1
    G_HAPPY = -2
    G_NORMAL = -3

    # natural order of affection groups
    _affg_order = [
        G_SAD,
        G_NORMAL,
        G_HAPPY
    ]

    # cascade map of affection groups
    # basically, given a group , which is the next group closet to Normal
    _affg_cascade_map = {
        G_SAD: G_NORMAL,
        G_HAPPY: G_NORMAL
    }

    # compare functions for affection / group
    def _compareAff(aff_1, aff_2):
        """
        See mas_compareAff for explanation
        """
        # it's pretty easy to tell if we have been given the same items
        if aff_1 == aff_2:
            return 0

        # otherwise, need to check for aff existence to get index
        if aff_1 not in _aff_order or aff_2 not in _aff_order:
            return 0

        # otherwise both proivded affections exist, lets index
        if _aff_order.index(aff_1) < _aff_order.index(aff_2):
            return -1

        return 1


    def _compareAffG(affg_1, affg_2):
        """
        See mas_compareAffG for explanation
        """
        # same stuff?
        if affg_1 == affg_2:
            return 0

        # check for aff group exist
        if affg_1 not in _affg_order or affg_2 not in _affg_order:
            return 0

        # otherwise, both groups exist, index
        if _affg_order.index(affg_1) < _affg_order.index(affg_2):
            return -1

        return 1


    def _betweenAff(aff_low, aff_check, aff_high):
        """
        checks if the given affection level is between the given low and high.
        See mas_betweenAff for explanation
        """
        aff_check = _aff_level_map.get(aff_check, None)

        # sanity checks
        if aff_check is None:
            # aff_check not a valid affection?
            return False
            
        # clean the affection compares
        aff_low = _aff_level_map.get(aff_low, None)
        aff_high = _aff_level_map.get(aff_high, None)

        if aff_low is None and aff_high is None:
            # if both items are None, we basically assume that both bounds
            # are set to unlimited.
            return True

        if aff_low is None:
            # dont care about the lower bound, so check if lower than
            # higher bound
            return _compareAff(aff_check, aff_high) <= 0

        if aff_high is None:
            # dont care about the upper bound, so check if higher than lower
            # bound
            return _compareAff(aff_check, aff_low) >= 0

        # otherwise, both low and high ranges are not None, so we
        # can actually check between the 2
        comp_low_high = _compareAff(aff_low, aff_high)
        if comp_low_high > 0:
            # low is actually greater than high. Therefore, the given
            # affection cannot possible be between the 2, probably.
            return False

        if comp_low_high == 0:
            # they are the same, just check for equivalence
            return _compareAff(aff_low, aff_check) == 0

        # otherwise, we legit need to check range
        return (
            _compareAff(aff_low, aff_check) <= 0
            and _compareAff(aff_check, aff_high) <= 0
        )


    def _isValidAff(aff_check):
        """
        Returns true if the given affection is a valid affection state

        NOTE: None is considered valid
        """
        if aff_check is None:
            return True

        return aff_check in _aff_level_map


    def _isValidAffRange(aff_range):
        """
        Returns True if the given aff range is a valid aff range.

        IN:
            aff_range - tuple of the following format:
                [0]: lower bound
                [1]: upper bound
            NOTE: Nones are considerd valid.
        """
        if aff_range is None:
            return True

        low, high = aff_range

        if not _isValidAff(low):
            return False

        if not _isValidAff(high):
            return False

        if low is None and high is None:
            return True

        return _compareAff(low, high) <= 0


    # thresholds values

    # Affection experience changer thresholds
    AFF_MAX_POS_TRESH = 100
    AFF_MIN_POS_TRESH = 30
    AFF_MIN_NEG_TRESH = -30
    AFF_MAX_NEG_TRESH = -75

    # Affection levels thresholds
    AFF_BROKEN_MIN = -100
    AFF_DISTRESSED_MIN = -75
    AFF_UPSET_MIN = -30
    AFF_HAPPY_MIN = 30
    AFF_AFFECTIONATE_MIN = 100
    AFF_ENAMORED_MIN = 400
    AFF_LOVE_MIN = 1000

    # Affection general mood threshold
    AFF_MOOD_HAPPY_MIN = 30
    AFF_MOOD_SAD_MIN = -30

    # lower affection cap for time
    AFF_TIME_CAP = -101


init -1 python in mas_affection:
    import os
    import datetime
    import store.mas_utils as mas_utils
    import store

    # affection log rotate
    #  we do rotations every 100 sessions
    if store.persistent._mas_affection_log_counter is None:
        # start counter if None
        store.persistent._mas_affection_log_counter = 0

    elif store.persistent._mas_affection_log_counter >= 500:
        # if 500 sessions, do a logrotate
        mas_utils.logrotate(
            os.path.normcase(renpy.config.basedir + "/log/"),
            "aff_log.txt"
        )
        store.persistent._mas_affection_log_counter = 0

    else:
        # otherwise increase counter
        store.persistent._mas_affection_log_counter += 1

    # affection log setup
    log = renpy.renpy.log.open("log/aff_log", append=True)
    log_open = log.open()
    log.raw_write = True

    # LOG messages
    # [current datetime]: monikatopic | magnitude | prev -> new
    _audit = "[{0}]: {1} | {2} | {3} -> {4}\n"

    # [current_datetime]: !FREEZE! | monikatopic | magnitude | prev -> new
    _audit_f = "[{0}]: {5} | {1} | {2} | {3} -> {4}\n"
    _freeze_text = "!FREEZE!"
    _bypass_text = "!BYPASS!"

    def audit(change, new, frozen=False, bypass=False, ldsv=None):
        """
        Audits a change in affection.

        IN:
            change - the amount we are changing by
            new - what the new affection value will be
            frozen - True means we were frozen, false measn we are not
            bypass - True means we bypassed, false means we did not
            ldsv - Set to the string to use instead of monikatopic
                NOTE: for load / save operations ONLY
        """
        if ldsv is None:
            piece_one = store.persistent.current_monikatopic
        else:
            piece_one = ldsv

        if frozen:

            # decide what piece 5 is
            if bypass:
                piece_five = _bypass_text
            else:
                piece_five = _freeze_text


            audit_text = _audit_f.format(
                datetime.datetime.now(),
                piece_one,
                change,
                store._mas_getAffection(),
                new,
                piece_five
            )

        else:
            audit_text = _audit.format(
                datetime.datetime.now(),
                piece_one,
                change,
                store._mas_getAffection(),
                new
            )

        log.write(audit_text)


    def raw_audit(old, new, change, tag):
        """
        Non affection-dependent auditing for general usage.

        IN:
            old - the "old" value
            new - the "new" value
            change - the chnage amount
            tag - a string to label this audit change
        """
        log.write(_audit.format(
            datetime.datetime.now(),
            tag,
            change,
            old,
            new
        ))


# need these utility functiosn post event_handler
init 15 python in mas_affection:
    import store # global
    import store.evhand as evhand
    import store.mas_selspr as mas_selspr
    import store.mas_layout as mas_layout
    persistent = renpy.game.persistent
    layout = store.layout

    # programming point order:
    # 1. affection state transition code is run
    # 2. Affection state is set
    # 3. affection group transition code is run
    # 4. Affection group is set
    #
    # if affection jumps over multiple states, we run the transition code
    # in order

    # programming points
##### [AFF010] AFFECTION PROGRAMMING POINTS ###################################
    # use these to do spoecial code stuffs
    def _brokenToDis():
        """
        Runs when transitioning from broken to distressed
        """
        # change quit message
        layout.QUIT_YES = mas_layout.QUIT_YES_DIS
        layout.QUIT_NO = mas_layout.QUIT_NO_UPSET
        layout.QUIT = mas_layout.QUIT

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _disToBroken():
        """
        Runs when transitioning from distressed to broken
        """
        # change quit message
        layout.QUIT_YES = mas_layout.QUIT_YES_BROKEN
        layout.QUIT_NO = mas_layout.QUIT_NO_BROKEN
        layout.QUIT = mas_layout.QUIT_BROKEN

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _disToUpset():
        """
        Runs when transitioning from distressed to upset
        """
        # change quit message
        layout.QUIT_YES = mas_layout.QUIT_YES

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _upsetToDis():
        """
        Runs when transitioning from upset to distressed
        """
        # change quit message
        layout.QUIT_YES = mas_layout.QUIT_YES_DIS
        if persistent._mas_acs_enable_promisering:
            renpy.store.monika_chr.remove_acs(renpy.store.mas_acs_promisering)
            persistent._mas_acs_enable_promisering = False

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _upsetToNormal():
        """
        Runs when transitioning from upset to normal
        """
        # change quit message
        layout.QUIT_NO = mas_layout.QUIT_NO

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _normalToUpset():
        """
        Runs when transitioning from normal to upset
        """
        # change quit message
        layout.QUIT_NO = mas_layout.QUIT_NO_UPSET

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _normalToHappy():
        """
        Runs when transitioning from noraml to happy
        """
        # change quit messages
        layout.QUIT_NO = mas_layout.QUIT_NO_HAPPY

        # enable text speed
        if persistent._mas_text_speed_enabled:
            store.mas_enableTextSpeed()

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _happyToNormal():
        """
        Runs when transitinong from happy to normal
        """
        # change quit messages
        layout.QUIT_NO = mas_layout.QUIT_NO

        # disable text speed
        store.mas_disableTextSpeed()

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _happyToAff():
        """
        Runs when transitioning from happy to affectionate
        """
        # change quit messages
        layout.QUIT_YES = mas_layout.QUIT_YES_AFF
        if persistent.gender == "M" or persistent.gender == "F":
            layout.QUIT_NO = mas_layout.QUIT_NO_AFF_G
        else:
            layout.QUIT_NO = mas_layout.QUIT_NO_AFF_GL
        layout.QUIT = mas_layout.QUIT_AFF

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _affToHappy():
        """
        Runs when transitioning from affectionate to happy
        """
        # change quit messages
        layout.QUIT_YES = mas_layout.QUIT_YES
        layout.QUIT_NO = mas_layout.QUIT_NO_HAPPY
        layout.QUIT = mas_layout.QUIT

        # revert nickname
        # TODO: we should actually push an event where monika asks player not
        # to call them a certain nickname. Also this change should probaly
        # happen from normal to upset instead since thats more indicative of
        # growing animosity toward someone
        # NOTE: maybe instead of pushing an event, we could also add a pool
        # event so player can ask what happened to the nickname
        persistent._mas_monika_nickname = "Monika"
        m_name = persistent._mas_monika_nickname

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _affToEnamored():
        """
        Runs when transitioning from affectionate to enamored
        """
        # unlock islands event if seen already
        if (
                store.seen_event("mas_monika_islands")
                and not store.mas_is_snowing
                and not store.mas_is_raining # TODO: rain versions
            ):
            if store.mas_cannot_decode_islands:
                # failed to decode islandds, delay this action
                store.mas_addDelayedAction(2)

                # lock the island event since we failed to decode images
                store.mas_lockEventLabel("mas_monika_islands")

            else:
                # otherwise we can directly unlock this topic
                store.mas_unlockEventLabel("mas_monika_islands")

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _enamoredToAff():
        """
        Runs when transitioning from enamored to affectionate
        """

        # remove island event delayed actions
        store.mas_removeDelayedActions(1, 2)

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _enamoredToLove():
        """
        Runs when transitioning from enamored to love
        """
        # change quit message
        layout.QUIT_NO = mas_layout.QUIT_NO_LOVE

        # unlock thanks compliement
        store.mas_unlockEventLabel("mas_compliment_thanks", eventdb=store.mas_compliments.compliment_database)

        # unlocks wardrobe if we have more than one clothes available
        if len(mas_selspr.filter_clothes(True)) > 1:
            store.mas_unlockEventLabel("monika_clothes_select")
            #TODO: Amend monika_outfit if > 1 outfit available.
            store.mas_lockEventLabel("monika_outfit")

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _loveToEnamored():
        """
        Runs when transitioning from love to enamored
        """
        # lock thanks compliment
        if store.seen_event("mas_compliment_thanks"):
            store.mas_lockEventLabel("mas_compliment_thanks", eventdb=store.mas_compliments.compliment_database)

        # always rebuild randos
        store.mas_idle_mailbox.send_rebuild_msg()


    def _gSadToNormal():
        """
        Runs when transitioning from sad group to normal group
        """
        return


    def _gNormalToSad():
        """
        Runs when transitioning from normal group to sad group
        """
        return


    def _gNormalToHappy():
        """
        Runs when transitioning from normal group to happy group
        """
        return


    def _gHappyToNormal():
        """
        Runs when transitioning from happy group to normal group
        """
        return

###############################################################################

    # transition programing point dict
    # each item has a tuple value:
    #   [0] - going up transition pp
    #   [1] - going down transition pp
    # if a tuple value is None, it doesn't have that pp
    #
    # The key should be the affection state you are COMING FROM
    _trans_pps = {
        BROKEN: (_brokenToDis, None),
        DISTRESSED: (_disToUpset, _disToBroken),
        UPSET: (_upsetToNormal, _upsetToDis),
        NORMAL: (_normalToHappy, _normalToUpset),
        HAPPY: (_happyToAff, _happyToNormal),
        AFFECTIONATE: (_affToEnamored, _affToHappy),
        ENAMORED: (_enamoredToLove, _enamoredToAff),
        LOVE: (None, _loveToEnamored)
    }

    # same as above, except for groups
    _transg_pps = {
        G_SAD: (_gSadToNormal, None),
        G_NORMAL: (_gNormalToHappy, _gNormalToSad),
        G_HAPPY: (None, _gHappyToNormal)
    }


    def runAffPPs(start_aff, end_aff):
        """
        Runs programming points to transition from the starting affection
        to the ending affection

        IN:
            start_aff - starting affection
            end_aff - ending affection
        """
        comparison = _compareAff(start_aff, end_aff)
        if comparison == 0:
            # dont do anything if same
            return

        # otherwise, now we need to do things
        start_index = _aff_order.index(start_aff)
        end_index = _aff_order.index(end_aff)
        if comparison < 0:
            for index in range(start_index, end_index):
                to_up, to_down = _trans_pps[_aff_order[index]]
                if to_up is not None:
                    to_up()

        else:
            for index in range(start_index, end_index, -1):
                to_up, to_down = _trans_pps[_aff_order[index]]
                if to_down is not None:
                    to_down()

        # finally, rebuild the event lists
        store.mas_rebuildEventLists()


    def runAffGPPs(start_affg, end_affg):
        """
        Runs programming points to transition from the starting affection group
        to the ending affection group

        IN:
            start_affg - starting affection group
            end_affg - ending affection group
        """
        comparison = _compareAffG(start_affg, end_affg)
        if comparison == 0:
            # dont do anything if same
            return

        # otherwise, now we need to do things
        start_index = _affg_order.index(start_affg)
        end_index = _affg_order.index(end_affg)
        if comparison < 0:
            for index in range(start_index, end_index):
                to_up, to_down = _transg_pps[_affg_order[index]]
                if to_up is not None:
                    to_up()

        else:
            for index in range(start_index, end_index, -1):
                to_up, to_down = _transg_pps[_affg_order[index]]
                if to_down is not None:
                    to_down()


    def _isMoniState(aff_1, aff_2, lower=False, higher=False):
        """
        Compares the given affection values according to the affection
        state system

        By default, this will check if aff_1 == aff_2

        IN:
            aff_1 - affection to compare
            aff_2 - affection to compare
            lower - True means we want to check aff_1 <= aff_2
            higher - True means we want to check aff_1 >= aff_2

        RETURNS:
            True if the given affections pass the test we want to do.
            False otherwise
        """
        comparison = _compareAff(aff_1, aff_2)

        if comparison == 0:
            return True

        if lower:
            return comparison <= 0

        if higher:
            return comparison >= 0

        return False


    def _isMoniStateG(affg_1, affg_2, lower=False, higher=False):
        """
        Compares the given affection groups according to the affection group
        system

        By default, this will check if affg_1 == affg_2

        IN:
            affg_1 - affection group to compare
            affg_2 - affection group to compare
            lower - True means we want to check affg_1 <= affg_2
            higher - True means we want to check affg_1 >= affg_2

        RETURNS:
            true if the given affections pass the test we want to do.
            False otherwise
        """
        comparison = _compareAffG(affg_1, affg_2)

        if comparison == 0:
            return True

        if lower:
            return comparison <= 0

        if higher:
            return comparison >= 0

        return False

    ### talk and play menu stuff
    # [AFF015]
    #
    # initial contributions by:
    #   @jmwall24
    #   @multimokia

    talk_menu_quips = dict()
    play_menu_quips = dict()

    def _init_talk_quips():
        """
        Initializes the talk quiplists
        """
        global talk_menu_quips
        def save_quips(_aff, quiplist):
            mas_ql = store.MASQuipList(allow_label=False)
            for _quip in quiplist:
                mas_ql.addLineQuip(_quip)
            talk_menu_quips[_aff] = mas_ql


        ## BROKEN quips
        quips = [
            "..."
        ]
        save_quips(BROKEN, quips)

        ## DISTRESSED quips
        quips = [
            "...Yes?",
            "...Oh?",
            "...Huh?",
            "...Hm?",
            "We can try talking, I guess.",
            "I guess we can talk.",
            "Oh... You want to talk?",
            "If you want to talk, go ahead.",
            "We can talk if you really want to.",
            "Are you sure you want to talk to me?",
            "You actually want to talk to me?"
        ]
        save_quips(DISTRESSED, quips)

        ## UPSET quips
        quips = [
            "What?",
            "What do you want?",
            "What now?",
            "What is it?",
            "Fine...we can talk.",
            "Just...whatever, go ahead."
        ]
        save_quips(UPSET, quips)

        ## NORMAL quips
        quips = [
            "What would you like to talk about?"
        ]
        save_quips(NORMAL, quips)

        ## HAPPY quips
        quips = [
            "What would you like to talk about?"
        ]
        save_quips(HAPPY, quips)

        ## AFFECTIONATE quips
        quips = [
            "What would you like to talk about? <3",
            "What would you like to talk about, [player]?",
            "Yes, [player]?",
            "What's on your mind, [player]?",
            "What would you like to talk about, [player]?"
        ]
        save_quips(AFFECTIONATE, quips)

        ## ENAMORED quips
        quips = [
            "What would you like to talk about? <3",
            "What would you like to talk about, honey?",
            "Yes, sweetheart?",
            "Yes, honey?",
            "Yes, dear?",
            "What's on your mind, darling?",
            "What would you like to talk about, sweetie?",
            "What would you like to talk about, [player]?",
            "Yes, [player]?",
            "What's on your mind, [player]?",
            "What would you like to talk about, [player]?"
        ]
        save_quips(ENAMORED, quips)

        ## LOVE quips
        quips = [
#            "Hey, what's up?",
            "What's on your mind?",
            "What's on your mind, darling?",
            "Anything on your mind?",
            "What's up, honey?",
            "What's up, dear?",
            "What's up, sweetie?",
#            "What's up?",
            "Yes, sweetheart?",
            "Yes, honey?",
            "Yes, dear?",
            "^_^",
            "<3",
            "Anything you'd like to talk about?",
            "We can talk about anything you like, [player]."
        ]
        save_quips(LOVE, quips)


    def _init_play_quips():
        """
        Initializes the play quipliust
        """
        global play_menu_quips
        def save_quips(_aff, quiplist):
            mas_ql = store.MASQuipList(allow_label=False)
            for _quip in quiplist:
                mas_ql.addLineQuip(_quip)
            play_menu_quips[_aff] = mas_ql


        ## BROKEN quips
        quips = [
            "..."
        ]
        save_quips(BROKEN, quips)

        ## DISTRESSED quips
        quips = [
            "...Sure.",
            "...Fine.",
            "I guess we can play a game.",
            "I guess, if you really want to.",
            "I suppose a game would be fine."
        ]
        save_quips(DISTRESSED, quips)

        ## UPSET quips
        quips = [
            "...Which game?",
            "Okay...whatever, choose a game.",
            "Fine, pick a game."
        ]
        save_quips(UPSET, quips)

        ## NORMAL quips
        quips = [
            "What would you like to play?",
            "What did you have in mind?",
            "Anything specific you'd like to play?"
        ]
        save_quips(NORMAL, quips)

        ## HAPPY quips
        quips = [
            "What would you like to play?",
            "What did you have in mind?",
            "Anything specific you'd like to play?"
        ]
        save_quips(HAPPY, quips)

        ## AFFECTIONATE quips
        quips = [
            "What would you like to play? <3",
            "Choose anything you like, [player].",
            "Pick anything you like, [player]."
        ]
        save_quips(AFFECTIONATE, quips)

        ## ENAMORED quips
        quips = [
            "What would you like to play? <3",
            "Choose anything you like, [player].",
            "Pick anything you like, [player].",
            "Choose anything you like, honey.",
            "Pick anything you like, sweetheart."
        ]
        save_quips(ENAMORED, quips)

        ## LOVE quips
        quips = [
            "What would you like to play? <3",
            "Choose anything you like, honey.",
            "Pick anything you like, sweetheart.",
            "Yay! Let's play together!",
            "I'd love to play something with you!",
            "I'd love to play with you!"
        ]
        save_quips(LOVE, quips)

    _init_talk_quips()
    _init_play_quips()


    def _dict_quip(_quips):
        """
        Returns a quip based on the current affection using the given quip
        dict

        IN:
            _quips - quip dict to pull from

        RETURNS:
            quip or empty string if failure
        """
        quipper = _quips.get(store.mas_curr_affection, None)
        if quipper is not None:
            return quipper.quip()

        return ""


    def talk_quip():
        """
        Returns a talk quip based on the current affection
        """
        quip = _dict_quip(talk_menu_quips)
        if len(quip) > 0:
            return quip
        return "What would you like to talk about?"


    def play_quip():
        """
        Returns a play quip based on the current affection
        """
        quip = _dict_quip(play_menu_quips)
        if len(quip) > 0:
            return quip
        return "What would you like to play?"



default persistent._mas_long_absence = False
default persistent._mas_pctaieibe = None
default persistent._mas_pctaneibe = None
default persistent._mas_pctadeibe = None
default persistent._mas_aff_backup = None

init -10 python:
    if persistent._mas_aff_mismatches is None:
        persistent._mas_aff_mismatches = 0

    def _mas_AffSave():
        aff_value = _mas_getAffection()
        #inum, nnum, dnum = mas_utils._splitfloat(aff_value)
        #persistent._mas_pctaieibe = bytearray(mas_utils._itoIS(inum))
        #persistent._mas_pctaneibe = bytearray(mas_utils._itoIS(nnum))
        #persistent._mas_pctadeibe = bytearray(mas_utils._itoIS(dnum))

        # reset
        persistent._mas_pctaieibe = None
        persistent._mas_pctaneibe = None
        persistent._mas_pctadeibe = None

        # audit this change
        store.mas_affection.audit(aff_value, aff_value, ldsv="SAVE")

        # backup this value
        if persistent._mas_aff_backup != aff_value:
            store.mas_affection.raw_audit(
                persistent._mas_aff_backup,
                aff_value,
                aff_value,
                "SET BACKUP"
            )
            persistent._mas_aff_backup = aff_value


    def _mas_AffLoad():
        #new_value = 0
        #if (
        #        persistent._mas_pctaieibe is not None
        #        and persistent._mas_pctaneibe is not None
        #        and persistent._mas_pctadeibe is not None
        #    ):
        #    try:
        #        inum = mas_utils._IStoi(
        #            mas_utils.ISCRAM.from_buffer(persistent._mas_pctaieibe)
        #        )
        #        nnum = mas_utils._IStoi(
        #            mas_utils.ISCRAM.from_buffer(persistent._mas_pctaneibe)
        #        )
        #        dnum = float(mas_utils._IStoi(
        #            mas_utils.ISCRAM.from_buffer(persistent._mas_pctadeibe)
        #        ))
        #        if inum < 0:
        #            new_value = inum - (nnum / dnum)
        #        else:
        #            new_value = inum + (nnum / dnum)
#
#            except:
#                # dont break me yo
#                new_value = 0
#
        # reset
        persistent._mas_pctaieibe = None
        persistent._mas_pctaneibe = None
        persistent._mas_pctadeibe = None

        # pull numerical afffection for audting
        if (
                persistent._mas_affection is None
                or "affection" not in persistent._mas_affection
            ):
            if persistent._mas_aff_backup is None:
                new_value = 0 
            else:
                new_value = persistent._mas_aff_backup

        else:
            new_value = persistent._mas_affection["affection"]

        # if the back is None, set the backup
        if persistent._mas_aff_backup is None:
            persistent._mas_aff_backup = new_value

            # audit
            store.mas_affection.raw_audit(
                "None",
                new_value,
                new_value,
                "NEW BACKUP"
            )


        else:
            # restore from backup if we have a mismatch
            if new_value != persistent._mas_aff_backup:
                persistent._mas_aff_mismatches += 1
                store.mas_affection.raw_audit(
                    new_value,
                    persistent._mas_aff_backup,
                    persistent._mas_aff_backup,
                    "RESTORE"
                )
                new_value = persistent._mas_aff_backup

        # audit this change
        store.mas_affection.audit(new_value, new_value, ldsv="LOAD")

        # and set what we got
        persistent._mas_affection["affection"] = new_value


# need to have affection initlaized post event_handler
init 20 python:

    import datetime
    import store.mas_affection as affection
    import store.mas_utils as mas_utils

    # Functions to freeze exp progression for story events, use wisely.
    def mas_FreezeGoodAffExp():
        persistent._mas_affection_goodexp_freeze = True

    def mas_FreezeBadAffExp():
        persistent._mas_affection_badexp_freeze = True

    def mas_FreezeBothAffExp():
        mas_FreezeGoodAffExp()
        mas_FreezeBadAffExp()

    def mas_UnfreezeBadAffExp():
        persistent._mas_affection_badexp_freeze = False

    def mas_UnfreezeGoodAffExp():
        persistent._mas_affection_goodexp_freeze = False

    def mas_UnfreezeBothExp():
        mas_UnfreezeBadAffExp()
        mas_UnfreezeGoodAffExp()


    # getter
    def _mas_getAffection():
        if persistent._mas_affection is not None:
            return persistent._mas_affection.get(
                "affection",
                persistent._mas_aff_backup
            )

        return persistent._mas_aff_backup


    def _mas_getBadExp():
        if persistent._mas_affection is not None:
            return persistent._mas_affection.get(
                "badexp",
                1
            )
        return 1


    def _mas_getGoodExp():
        if persistent._mas_affection is not None:
            return persistent._mas_affection.get(
                "goodexp",
                1
            )
        return 1


    def _mas_getTodayExp():
        if persistent._mas_affection is not None:
            return persistent._mas_affection.get("today_exp", 0)

        return 0
    

    # numerical affection check
    def mas_isBelowZero():
        return _mas_getAffection() < 0


    ## affection comparison
    # [AFF020] Affection comparTos
    def mas_betweenAff(aff_low, aff_check, aff_high):
        """
        Checks if the given affection is between the given affection levels.

        If low is actually greater than high, then False is always returned

        IN:
            aff_low - the lower bound of affecton to check with (inclusive)
                if None, then we assume no lower bound
            aff_check - the affection to check
            aff_high - the upper bound of affection to check with (inclusive)
                If None, then we assume no upper bound

        RETURNS:
            True if the given aff check is within the bounds of the given
            lower and upper affection limits, False otherwise.
            If low is greater than high, False is returned.
        """
        return affection._betweenAff(aff_low, aff_check, aff_high)


    def mas_compareAff(aff_1, aff_2):
        """
        Runs compareTo logic on the given affection states

        IN:
            aff_1 - an affection state to compare
            aff_2 - an affection state to compare

        RETURNS:
            negative number if aff_1 < aff_2
            0 if aff_1 == aff_2
            postitive number if aff_1 > aff_2
            Returns 0 if a non affection state was provided
        """
        return affection._compareAff(aff_1, aff_2)


    def mas_compareAffG(affg_1, affg_2):
        """
        Runs compareTo logic on the given affection groups

        IN:
            affg_1 - an affection group to compare
            affg_2 - an affection group to compare

        RETURNS:
            negative number if affg_1 < affg_2
            0 if affg_1 == affg_2
            positive numbre if affg_1 > affg_2
            Returns 0 if a non affection group was provided
        """
        return affection._compareAffG(affg_1, affg_2)


    ## afffection state functions
    # [AFF021] Affection state comparisons
    def mas_isMoniBroken(lower=False, higher=False):
        """
        Checks if monika is broken

        IN:
            lower - True means we include everything below this affection state
                as broken as well
                (Default: False)
            higher - True means we include everything above this affection
                state as broken as well
                (Default: False)

        RETURNS:
            True if monika is broke, False otherwise
        """
        return affection._isMoniState(
            mas_curr_affection,
            store.mas_affection.BROKEN,
            higher=higher
        )


    def mas_isMoniDis(lower=False, higher=False):
        """
        Checks if monika is distressed

        IN:
            lower - True means we cinlude everything below this affection state
                as distressed as well
                NOTE: takes precedence over higher
                (Default: False)
            higher - True means we include everything above this affection
                state as distressed as well
                (Default: FAlse)

        RETURNS:
            True if monika is distressed, false otherwise
        """
        return affection._isMoniState(
            mas_curr_affection,
            store.mas_affection.DISTRESSED,
            lower=lower,
            higher=higher
        )


    def mas_isMoniUpset(lower=False, higher=False):
        """
        Checks if monika is upset

        IN:
            lower - True means we include everything below this affection
                state as upset as well
                (Default: False)
            higher - True means we include everything above this affection
                state as upset as well
                (Default: False)

        RETURNS:
            True if monika is upset, false otherwise
        """
        return affection._isMoniState(
            mas_curr_affection,
            store.mas_affection.UPSET,
            lower=lower,
            higher=higher
        )


    def mas_isMoniNormal(lower=False, higher=False):
        """
        Checks if monika is normal

        IN:
            lower - True means we include everything below this affection state
                as normal as well
                (Default: False)
            higher - True means we include evreything above this affection
                state as normal as well
                (Default: False)

        RETURNS:
            True if monika is normal, false otherwise
        """
        return affection._isMoniState(
            mas_curr_affection,
            store.mas_affection.NORMAL,
            lower=lower,
            higher=higher
        )


    def mas_isMoniHappy(lower=False, higher=False):
        """
        Checks if monika is happy

        IN:
            lower - True means we include everything below this affection
                state as happy as well
                (Default: False)
            higher - True means we include everything above this affection
                state as happy as well
                (Default: False)

        RETURNS:
            True if monika is happy, false otherwise
        """
        return affection._isMoniState(
            mas_curr_affection,
            store.mas_affection.HAPPY,
            lower=lower,
            higher=higher
        )


    def mas_isMoniAff(lower=False, higher=False):
        """
        Checks if monika is affectionate

        IN:
            lower - True means we include everything below this affection
                state as affectionate as well
                (Default: FAlse)
            higher - True means we include everything above this affection
                state as affectionate as well
                (Default: False)

        RETURNS:
            True if monika is affectionate, false otherwise
        """
        return affection._isMoniState(
            mas_curr_affection,
            store.mas_affection.AFFECTIONATE,
            lower=lower,
            higher=higher
        )


    def mas_isMoniEnamored(lower=False, higher=False):
        """
        Checks if monika is enamored

        IN:
            lower - True means we include everything below this affection
                state as enamored as well
                (Default: False)
            higher - True means we include everything above this affection
                state as enamored as well
                (Default: False)

        RETURNS:
            True if monika is enamored, false otherwise
        """
        return affection._isMoniState(
            mas_curr_affection,
            store.mas_affection.ENAMORED,
            lower=lower,
            higher=higher
        )


    def mas_isMoniLove(lower=False, higher=False):
        """
        Checks if monika is in love

        IN:
            lower - True means we include everything below this affectionate
                state as love as well
                (Default: False)
            higher - True means we include everything above this affection
                state as love as well
                (Default: False)

        RETURNS:
            True if monika in love, false otherwise
        """
        return affection._isMoniState(
            mas_curr_affection,
            store.mas_affection.LOVE,
            lower=lower
        )


    # [AFF023] Group state checkers
    def mas_isMoniGSad(lower=False, higher=False):
        """
        Checks if monika is in sad affection group

        IN:
            lower - True means we include everything below this affection
                group as sad as well
                (Default: False)
            higher - True means we include everything above this affection
                group as sad as well
                (Default: False)

        RETURNS:
            True if monika in sad group, false otherwise
        """
        return affection._isMoniStateG(
            mas_curr_affection_group,
            store.mas_affection.G_SAD,
            higher=higher
        )


    def mas_isMoniGNormal(lower=False, higher=False):
        """
        Checks if monika is in normal affection group

        IN:
            lower - True means we include everything below this affection
                group as normal as well
                (Default: False)
            higher - True means we include everything above this affection
                group as normal as well
                (Default: False)

        RETURNS:
            True if monika is in normal group, false otherwise
        """
        return affection._isMoniStateG(
            mas_curr_affection_group,
            store.mas_affection.G_NORMAL,
            lower=lower,
            higher=higher
        )


    def mas_isMoniGHappy(lower=False, higher=False):
        """
        Checks if monika is in happy affection group

        IN:
            lower - True means we include everything below this affection
                group as happy as well
                (Default: False)
            higher - True means we include everything above this affection
                group as happy as well
                (Default: FAlse)

        RETURNS:
            True if monika is in happy group, false otherwise
        """
        return affection._isMoniStateG(
            mas_curr_affection_group,
            store.mas_affection.G_HAPPY,
            lower=lower
        )


   # Used to adjust the good and bad experience factors that are used to adjust affection levels.
    def mas_updateAffectionExp(skipPP=False):
        global mas_curr_affection
        global mas_curr_affection_group

        # store the value for easiercomparisons
        curr_affection = _mas_getAffection()

        # If affection is between AFF_MIN_POS_TRESH and AFF_MAX_POS_TRESH, update good exp. Simulates growing affection.
        if  affection.AFF_MIN_POS_TRESH <= curr_affection < affection.AFF_MAX_POS_TRESH:
            persistent._mas_affection["goodexp"] = 3
            persistent._mas_affection["badexp"] = 1

        # If affection is more than AFF_MAX_TRESH, update good exp. Simulates increasing affection.
        elif curr_affection >= affection.AFF_MAX_POS_TRESH:
            persistent._mas_affection["goodexp"] = 3

        # If affection is between AFF_MAX_NEG_TRESH and AFF_MIN_NEG_TRESH, update both exps. Simulates erosion of affection.
        elif affection.AFF_MAX_NEG_TRESH < curr_affection <= affection.AFF_MIN_NEG_TRESH:
            persistent._mas_affection["goodexp"] = 0.5
            persistent._mas_affection["badexp"] = 3

        # If affection is less than AFF_MIN_NEG_TRESH, update bad exp. Simulates increasing loss of affection.
        elif curr_affection <= affection.AFF_MAX_NEG_TRESH:
            persistent._mas_affection["badexp"] = 5

        # Defines an easy current affection statement to refer to so points aren't relied upon.
        new_aff = mas_curr_affection
        if curr_affection <= affection.AFF_BROKEN_MIN:
            new_aff = affection.BROKEN

        elif affection.AFF_BROKEN_MIN < curr_affection <= affection.AFF_DISTRESSED_MIN:
            new_aff = affection.DISTRESSED

        elif affection.AFF_DISTRESSED_MIN < curr_affection <= affection.AFF_UPSET_MIN:
            new_aff = affection.UPSET

        elif affection.AFF_UPSET_MIN < curr_affection < affection.AFF_HAPPY_MIN:
            new_aff = affection.NORMAL

        elif affection.AFF_HAPPY_MIN <= curr_affection < affection.AFF_AFFECTIONATE_MIN:
            new_aff = store.mas_affection.HAPPY

        elif affection.AFF_AFFECTIONATE_MIN <= curr_affection < affection.AFF_ENAMORED_MIN:
            new_aff = affection.AFFECTIONATE

        elif affection.AFF_ENAMORED_MIN <= curr_affection < affection.AFF_LOVE_MIN:
            new_aff = affection.ENAMORED

        elif curr_affection >= affection.AFF_LOVE_MIN:
            new_aff = affection.LOVE

        # run affection programming points
        if new_aff != mas_curr_affection:
            if not skipPP:
                affection.runAffPPs(mas_curr_affection, new_aff)
            mas_curr_affection = new_aff

        # A group version for general sadness or happiness
        new_affg = mas_curr_affection_group
        if curr_affection <= affection.AFF_MOOD_SAD_MIN:
            new_affg = affection.G_SAD

        elif curr_affection >= affection.AFF_MOOD_HAPPY_MIN:
            new_affg = affection.G_HAPPY

        else:
            new_affg = affection.G_NORMAL

        if new_affg != mas_curr_affection_group:
            if not skipPP:
                affection.runAffGPPs(mas_curr_affection_group, new_affg)
            mas_curr_affection_group = new_affg


    # Used to increment affection whenever something positive happens.
    def mas_gainAffection(
            amount=None,
            modifier=1,
            bypass=False
        ):

        if amount is None:
            amount = _mas_getGoodExp()

        # is it a new day?
        if persistent._mas_affection.get("freeze_date") is None or datetime.date.today() > persistent._mas_affection["freeze_date"]:
            persistent._mas_affection["freeze_date"] = datetime.date.today()
            persistent._mas_affection["today_exp"] = 0
            mas_UnfreezeGoodAffExp()

        # calculate new value
        frozen = persistent._mas_affection_goodexp_freeze
        change = (amount * modifier)
        new_value = _mas_getAffection() + change
        if new_value > 1000000:
            new_value = 1000000

        # audit the attempted change
        affection.audit(change, new_value, frozen, bypass)

        # if we're not freezed or if the bypass flag is True
        if not frozen or bypass:
            # Otherwise, use the value passed in the argument.
            persistent._mas_affection["affection"] = new_value

            if not bypass:
                persistent._mas_affection["today_exp"] = (
                    _mas_getTodayExp() + change
                )
                if persistent._mas_affection["today_exp"] >= 7:
                    mas_FreezeGoodAffExp()

            # Updates the experience levels if necessary.
            mas_updateAffectionExp()


    # Used to subtract affection whenever something negative happens.
    # A reason can be specified and used for the apology dialogue
    # if the default value is used Monika won't comment on the reason,
    # and slightly will recover affection
    # if None is passed she won't acknowledge that there was need for an apology.
    # DEFAULTS reason to an Empty String mostly because when this one is called
    # is intended to be used for something the player can apologize for, but it's
    # not totally necessary.
    #NEW BITS:
    #prompt: the prompt shown in the menu for apologizing
    #expirydatetime: 
    #generic: do we want this to be persistent? or not
    def mas_loseAffection(
            amount=None,
            modifier=1,
            reason=None,
            ev_label=None,
            apology_active_expiry=datetime.timedelta(hours=3),
            apology_overall_expiry=datetime.timedelta(weeks=1)
        ):

        if amount is None:
            amount = _mas_getBadExp()

        #set apology flag
        mas_setApologyReason(reason=reason,ev_label=ev_label,apology_active_expiry=apology_active_expiry,apology_overall_expiry=apology_overall_expiry)

        # calculate new vlaue
        frozen = persistent._mas_affection_badexp_freeze
        change = (amount * modifier)
        new_value = _mas_getAffection() - change
        if new_value < -1000000:
            new_value = -1000000

        # audit this attempted change
        affection.audit(change, new_value, frozen)

        if not frozen:
            # Otherwise, use the value passed in the argument.
            persistent._mas_affection["affection"] = new_value

            # Updates the experience levels if necessary.
            mas_updateAffectionExp()


    def mas_setAffection(
            amount=None
        ):
        # NOTE: never use this to add / lower affection unless its to
        #   strictly set affection to a level for some reason.
#        frozen = (
#            persistent._mas_affection_badexp_freeze
#            or persistent._mas_affection_goodexp_freeze
#        )
        if amount is None:
            amount = _mas_getAffection()

        # audit the change (or attempt)
        affection.audit(amount, amount, False)

        # NOTE: we should NEVER freeze set affection. 
        # Otherwise, use the value passed in the argument.
        persistent._mas_affection["affection"] = amount
        # Updates the experience levels if necessary.
        mas_updateAffectionExp()

    def mas_setApologyReason(
        reason=None,
        ev_label=None,
        apology_active_expiry=datetime.timedelta(hours=3),
        apology_overall_expiry=datetime.timedelta(weeks=1)
        ):
        """
        Sets a reason for apologizing

        IN:
            reason - The reason for the apology (integer value corresponding to item in the apology_reason_db)
                (if left None, and an ev_label is present, we assume a non-generic apology)
            ev_label - The apology event we want to unlock
                (required)
            apology_active_expiry - The amount of session time after which, the apology that was added expires
                defaults to 3 hours active time
            apology_overall_expiry - The amount of overall time after which, the apology that was added expires
                defaults to 7 days
        """

        global mas_apology_reason

        if ev_label is None:
            if reason is None:
                mas_apology_reason = 0
            else:
                mas_apology_reason = reason
            return
        elif mas_getEV(ev_label) is None:
            store.mas_utils.writelog(
                "[ERROR]: ev_label does not exist: {0}\n".format(repr(ev_label))
            )
            return

        if ev_label not in persistent._mas_apology_time_db:
            #Unlock the apology ev label
            store.mas_unlockEVL(ev_label, 'APL')

            #Calculate the current total playtime
            current_total_playtime = persistent.sessions['total_playtime'] + mas_getSessionLength()

            #Now we set up our apology dict to keep track of this so we can relock it if you didn't apologize in time
            persistent._mas_apology_time_db[ev_label] = (current_total_playtime + apology_active_expiry,datetime.date.today() + apology_overall_expiry)
            return

    # Used to check to see if affection level has reached the point where it should trigger an event while playing the game.
    def mas_checkAffection():

        curr_affection = _mas_getAffection()
        # If affection level between -15 and -20 and you haven't seen the label before, push this event where Monika mentions she's a little upset with the player.
        # This is an indicator you are heading in a negative direction.
        if curr_affection <= -15 and not seen_event("mas_affection_upsetwarn"):
            pushEvent("mas_affection_upsetwarn")

        # If affection level between 15 and 20 and you haven't seen the label before, push this event where Monika mentions she's really enjoying spending time with you.
        # This is an indicator you are heading in a positive direction.
        elif 15 <= curr_affection and not seen_event("mas_affection_happynotif"):
            pushEvent("mas_affection_happynotif")

        # If affection level is greater than 100 and you haven't seen the label yet, push this event where Monika will allow you to give her a nick name.
        elif curr_affection >= 100 and not seen_event("monika_affection_nickname"):
            pushEvent("monika_affection_nickname")

        # If affection level is less than -50 and the label hasn't been seen yet, push this event where Monika says she's upset with you and wants you to apologize.
        elif curr_affection <= -50 and not seen_event("mas_affection_apology"):
            if not persistent._mas_disable_sorry:
                pushEvent("mas_affection_apology")
        # If affection level is equal or less than -100 and the label hasn't been seen yet, push this event where Monika says she's upset with you and wants you to apologize.
        elif curr_affection <= -100 and not seen_event("greeting_tears"):
            mas_unlockEVL("greeting_tears", "GRE")

    # Easy functions to add and subtract points, designed to make it easier to sadden her so player has to work harder to keep her happy.
    # Check function is added to make sure mas_curr_affection is always appropriate to the points counter.
    # Internal cooldown to avoid topic spam and Monika affection swings, the amount of time to wait before a function is effective
    # is equal to the amount of points it's added or removed in minutes.

    # Nothing to apologize for now
    mas_apology_reason = None

    def _mas_AffStartup():
        # need to load affection values from beyond the grave
        # failure to load means we reset to 0. No excuses
        _mas_AffLoad()

        # Makes the game update affection on start-up so the global variables
        # are defined at all times.
        mas_updateAffectionExp()

        if persistent.sessions["last_session_end"] is not None:
            persistent._mas_absence_time = (
                datetime.datetime.now() -
                persistent.sessions["last_session_end"]
            )
        else:
            persistent._mas_absence_time = datetime.timedelta(days=0)

        # Monika's initial affection based on start-up.
        if not persistent._mas_long_absence:
            time_difference = persistent._mas_absence_time
            # we skip this for devs since we sometimes use older
            # persistents and only apply after 1 week
            if (
                    not config.developer
                    and time_difference >= datetime.timedelta(weeks = 1)
                ):
                new_aff = _mas_getAffection() - (
                    0.5 * time_difference.days
                )
                if new_aff < affection.AFF_TIME_CAP:
                    if (
                            time_difference >= datetime.timedelta(
                                days=(365 * 10)
                            )
                        ):
                        # 10 years later is an end-game situation
                        mas_loseAffection(200)

                    else:
                        # otherwise, you cant lose past a certain amount
                        mas_setAffection(affection.AFF_TIME_CAP)

                else:
                    mas_setAffection(new_aff)


# Unlocked when affection level reaches 50.
# This allows the player to choose a nick name for Monika that will be displayed on the label where Monika's name usually is.
# There is a character limit of 10 characters.
init 5 python:
    addEvent(
        Event(persistent.event_database,
            eventlabel='monika_affection_nickname',
            prompt="Infinite Monikas",
            category=['monika'],
            random=False,
            pool=True,
            unlocked=True,
            rules={"no unlock": None},
            aff_range=(mas_aff.AFFECTIONATE, None)
        )
    )

default persistent._mas_called_moni_a_bad_name = False
default persistent._mas_offered_nickname = False

label monika_affection_nickname:
    python:
        import re

        # NOTE: consider if we should read this from a file instead
        bad_nickname_list = [
            "annoying",
            "anus",
            "arrogant",
            "atrocious",
            "awful",
            "bitch",
            "blood",
            "boob",
            "boring",
            "bulli",
            "bully",
            "bung",
            "butt",
            "conceited",
            "corrupt",
            "cougar",
            "crap",
            "creepy",
            "criminal",
            "cruel",
            "cunt",
            "damn",
            "demon",
            "dick",
            "dirt",
            "disgusting",
            "douche",
            "dumb",
            "egotistical",
            "evil",
            "fake",
            "fetus",
            "filth",
            "foul",
            "fuck",
            "garbage",
            "gay",
            "gey",
            "gross",
            "gruesome",
            "hate",
            "heartless",
            "hideous",
            "^ho$",
            "^hoe$",
            "hore",
            "horrible",
            "horrid",
            "hypocrite",
            "immoral",
            "irritating",
            "jerk",
            "junk",
            "kill",
            "kunt",
            "lesbo",
            "lesbian",
            "lezbo",
            "lezbian",
            "liar",
            "loser",
            "maniac",
            "milf",
            "monster",
            "moron",
            "murder",
            "narcissist",
            "nasty",
            "Natsuki",
            "nefarious",
            "nigga",
            "nigger",
            "pad",
            "pantsu",
            "panti",
            "panty",
            "pedo",
            "penis",
            "plaything",
            "poison",
            "porn",
            "pretentious",
            "psycho",
            "puppet",
            "pussy",
            "rape",
            "repulsive",
            "retard",
            "rump",
            "sadist",
            "Sayori",
            "scum",
            "selfish",
            "shit",
            "sick",
            "slaughter",
            "slave",
            "slut",
            "sociopath",
            "soil",
            "stink",
            "stupid",
            "tampon",
            "teabag",
            "terrible",
            "thot",
            "^tit$",
            "tits",
            "titt",
            "tool",
            "torment",
            "torture",
            "toy",
            "trap",
            "trash",
            "troll",
            "ugly",
            "useless",
            "vain",
            "vile",
            "waste",
            "whore",
            "wicked",
            "witch",
            "worthless",
            "wrong",
            "Yuri",
        ]

        # TODO: potential special responses for:
        # okasa (OKASA MONIKA)
        # imouto
        # nee-chan
        # maybe more?
        good_nickname_list = [
            "angel",
            "beautiful",
            "best",
            "cuddl",
            "cute",
            "可愛い",
            "cutie",
            "darling",
            "great"
            "heart",
            "honey",
            "love",
            "Mon",
            "Moni",
            "princess",
            "sweet",
        ]

        # mom list
        mom_nickname_list = [
            "mom",
            "momma",
            "mother",
            "momika",
            "mama",
            "mommy",
            "okasan",
            "okaasan",
            "kaasan",
            "kasan",
        ]

        # for later code
        aff_nickname_ev = mas_getEV("monika_affection_nickname")

    if not persistent._mas_offered_nickname:
        m 1euc "I've been thinking, [player]..."
        m 3eud "You know how there are potentially infinite Monikas right?"
        if renpy.seen_label('monika_clones'):
            m 3eua "We did discuss this before after all."
        m 3hua "Well, I thought of a solution!"
        m 3eua "Why don't you give me a nickname? It'd make me the only Monika in the universe with that name."
        m 3eka "And it would mean a lot if you choose one for me~"
        m 3hua "I'll still get the final say, though!"
        m "What do you say?"
        python:
            # change the prompt for this event
            aff_nickname_ev.prompt = "Can I call you a different name?"
            Event.lockInit("prompt", ev=aff_nickname_ev)
            persistent._mas_offered_nickname = True

    else:
        jump monika_affection_nickname_yes

    menu:
        m "What do you say?{fast}"
        "Yes.":
            label monika_affection_nickname_yes:
                pass
            $ bad_nickname_search = re.compile('|'.join(bad_nickname_list), re.IGNORECASE)
            $ good_nickname_search = re.compile('|'.join(good_nickname_list), re.IGNORECASE)
            $ done = False
            m 1eua "Okay! Just type 'Nevermind' if you change your mind, [player]."
            while not done:
                $ inputname = renpy.input("So what do you want to call me?",allow=" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_",length=10).strip(' \t\n\r')
                $ lowername = inputname.lower()
                # lowername isn't detecting player or m_name?
                if lowername == "nevermind":
                    m 1euc "Oh, I see."
                    m 1tkc "Well...that's a shame."
                    m 3eka "But that's okay. I like '[m_name]' anyway."
                    $ done = True
                elif not lowername:
                    m 1lksdla "..."
                    m 1hksdrb "You have to give me a name, [player]!"
                    m "I swear you're just so silly sometimes."
                    m 1eka "Try again!"
                elif lowername == player.lower():
                    m 1euc "..."
                    m 1lksdlb "That's your name, [player]! Give me my own!"
                    m 1eka "Try again~"
                elif lowername == m_name.lower():
                    m 1euc "..."
                    m 1hksdlb "I thought we were choosing a new name, silly."
                    m 1eka "Try again~"
                elif lowername in mom_nickname_list:
                    # mother flow
                    m 1tku "Oh, you're a momma's boy, huh?"
                    $ persistent._mas_monika_nickname = inputname
                    $ m_name = inputname

                    m 2tfu "I'll be your mommy."
                    $ done = True

                else:
                    $ bad_nickname = bad_nickname_search.search(inputname)
                    if bad_nickname is None:
                        $ good_nickname = good_nickname_search.search(inputname)
                        if inputname == "Monika":
                            m 1eua "Ehehe~ Back to the classics, I see."
                        elif good_nickname is None:
                            m 1eud "Well, it's not exactly my favorite."
                            m 1eua "But I don't dislike it either."
                            m 1rfu "[inputname]... Yeah, I'm starting to like it a bit more."
                        else:
                            m 1wuo "Oh! That's a wonderful name!"
                            m 3ekbfa "Thank you, [player]. You're such a sweetheart~!"
                        $ persistent._mas_monika_nickname = inputname
                        $ m_name = inputname
                        m 2eua "Okay, [player]!"
                        if m_name == "Monika":
                            m 1hua "I'll go back to my name, then."
                        else:
                            m 3hua "From now on, you can call me {i}'[m_name]'{/i}."
                            m 1hub "Ehehe~"
                        $ done = True
                    else:
                        #Remove the apology reason from this as we're handling the apology differently now.
                        $ mas_loseAffection(ev_label="mas_apology_bad_nickname")
                        if lowername == "yuri" or lowername == "sayori" or lowername == "natsuki":
                            m 1wud "...!"
                            m 2wfw "I..."
                            m "I...can't believe you just did that, [player]."
                            m 2wfx "Are you really trying to give me her name?"
                            m 2dfd ".{w=0.5}.{w=0.5}.{w=0.5}{nw}"
                            m 2dfc ".{w=0.5}.{w=0.5}.{w=0.5}{nw}"
                            m 2rkc "I thought you..."
                            m 2dfc "..."
                            m 2lfc "I can't believe this, [player]"
                            m 2dfc "..."
                            m 2lfc "That really hurt."
                            m "A lot more than what you can imagine."
                            if mas_getEV('mas_apology_bad_nickname').shown_count == 2:
                                call monika_affection_nickname_bad_lock

                            show monika 1efc
                            pause 5.0
                        else:
                            m 4efd "[player]! That's not nice at all!"
                            m 2efc "Why would you say such things?"
                            m 2rfw "If you didn't want to do this, you should've just said so!"
                            m 2dftdc "..."
                            m 2ektsc "...You didn't have to be so mean."
                            m 2dftdc "That really hurt, [player]."

                            if  mas_getEV('mas_apology_bad_nickname').shown_count == 2:
                                call monika_affection_nickname_bad_lock
                            else:
                                m 2efc "Please don't do that again."
                        $ persistent._mas_called_moni_a_bad_name = True

                        #reset nickname if not Monika
                        if m_name.lower() != "monika":
                            $ m_name = "Monika"
                            $ persistent._mas_monika_nickname = "Monika"

                        $ mas_lockEventLabel("monika_affection_nickname")
                        $ done = True

        "No.":
            m 1ekc "Oh..."
            m 1lksdlc "Alright then, if you say so."
            m 3eka "Just tell me if you ever change your mind, [player]."
            $ done = True
    return

label monika_affection_nickname_bad_lock:
    m 2efc "Forget about this idea."
    m "It seems it was a mistake."
    m 1efc "Let's talk about something else."
    return

# Event to warn player that Monika feels like she's not receiving the affection she deserves.
label mas_affection_upsetwarn:
    m 1dsc "Hey, [player]..."
    m 1lksdlc "Recently, I've been feeling like my love and affection that I give is being...ignored."
    m 1dsc "I feel like you're giving me less and less of your love..."
    m 1dsd "I thought I'd let you know how I feel. After all, communication is the key to a strong relationship, right?"
    m 1eka "I hope there's nothing wrong between us, [player]."
    return

# Event to indicate that Monika is happy to be receiving your affection.
label mas_affection_happynotif:
    m 1hua "Hey, [player]!"
    m 1eua "I just wanted to say thank you for being such a wonderful person."
    m 1ekbfa "The fact that you give me so much of your love means a lot to me. I really don't know where I'd be without you."
    m 1dubsu "I love you, [player]. Let's be like this forever~"
    return


define mas_finalfarewell_mode = False

# prepwork for the finalfarewell
label mas_affection_finalfarewell_start:
    call spaceroom(hide_monika=True)
    show emptydesk zorder MAS_MONIKA_Z at i11
    show mas_finalnote_idle zorder 11

    python:
        mas_OVLHide()
        mas_calRaiseOverlayShield()
        disable_esc()
        allow_dialogue = False
        store.songs.enabled = False
        mas_finalfarewell_mode = True
        layout.QUIT = glitchtext(20)


    jump mas_affection_finalfarewell

# this will loop through the final poem everytime!
label mas_affection_finalfarewell:

    python:
        ui.add(MASFinalNoteDisplayable())
        scratch_var = ui.interact()

    call showpoem(poem_finalfarewell, music=False,paper="mod_assets/poem_assets/poem_finalfarewell.png")

    menu:
        "I'm sorry.":
            pass
        "...":
            pass

    jump mas_affection_finalfarewell


init python:

    # custom displayabe for the poem screen
    class MASFinalNoteDisplayable(renpy.Displayable):
        import pygame # mouse stuff

        # CONSTANTS
        POEM_WIDTH = 200
        POEM_HEIGHT= 73

        MOUSE_EVENTS = (
            pygame.MOUSEMOTION,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEBUTTONDOWN
        )

        def __init__(self):
            """
            Creates the final poem displayable
            """
            super(renpy.Displayable, self).__init__()

            # final poem is a button
            paper_idle = Image("mod_assets/poem_finalfarewell_desk.png")
            paper_hover = Image("mod_assets/poem_finalfarewell_desk_select.png")

            # no button text
            empty_button_text = Text("")

            # calculate paper location
            paper_x = int((1280 - self.POEM_WIDTH) / 2)
            paper_y = int(720 - self.POEM_HEIGHT)

            # build the paper as a button
            self._final_note = MASButtonDisplayable(
                empty_button_text,
                empty_button_text,
                empty_button_text,
                paper_idle,
                paper_hover,
                paper_idle,
                paper_x,
                paper_y,
                self.POEM_WIDTH,
                self.POEM_HEIGHT
            )


        def render(self, width, height, st, at):
            """
            Render function
            """
            r = renpy.Render(width, height)

            # render the paper
            r.blit(
                self._final_note.render(width, height, st, at),
                (self._final_note.xpos, self._final_note.ypos)
            )

            return r


        def event(self, ev, x, y, st):
            """
            Event function
            """
            if (
                    ev.type in self.MOUSE_EVENTS
                    and self._final_note.event(ev, x, y, st)
                ):
                return True

            renpy.redraw(self, 0)
            raise renpy.IgnoreEvent()

label mas_affection_apology:
    m 2dfc "[player]..."
    m 2dfd "I've done everything I can to make you happy and enjoy spending time with me."
    m 2efc "But all you've given me back is pain..."
    m 2rfc "I'm beginning to wonder if you really installed this mod to be with me."
    m 2dsc "Perhaps you brought me back just to toy with me?"
    m 2efc "Or maybe you're doing this intentionally to see what happens?"
    m 2lfc "Regardless, I'm giving you an ultimatum."
    m "I can't let this go any further, [player]."
    m 2lfc "If you really are sorry, write me a note called {i}imsorry{/i}, and place it in the DDLC directory." #Maybe put it in the character folder instead?
    m 2dfd "Until then, goodbye..."
    $ persistent._mas_affection["apologyflag"] = True
    return 'quit'

label mas_affection_noapology:
    m 2efd "You still haven't written me a note called {i}imsorry{/i}  in the DDLC directory."
    m 2efc "Until then, I don't want to talk to you."
    jump _quit

label mas_affection_yesapology:
    m 1eka "Thank you, [player]. I accept your apology."
    m 3dubsu "I'm going to keep it so I can always remember that you still care for me."
    m 1ekc "But please be more considerate of my feelings from now on."
    m 2eka "I love you so much and you mean the world to me, [player]."
    m 1duu "Thank you for putting my heart at ease~"
    show monika 1esa
    $ mas_DropShield_core()
    $ set_keymaps()
    jump ch30_preloop

label mas_affection_apologydeleted:
    $ mas_loseAffection(modifier=3)
    m 1wud "..."
    m 2efd "[player], did you delete the apology note I wanted to keep?"
    m "Why would you do that? Are you not {i}really{/i} sorry?"
    m 2dfc "..."
    m 2efc "Write me a new one, [player]."
    jump _quit

#Surprise txt functions.
init python:

    def _write_txt(path,text,update=False):
        """
        Writes the text file in the specified path using basedir as starting path

        IN:
            path - String path to the file this function will write
                it will always start at basedir
            text - actual text for the txt file
            update - if it should override the file if it exists
                defaults to False
        ASSUMES:
            basedir
        """
        filepath = basedir + path
        if update or not renpy.exists(filepath):
            with open(filepath, "w") as note:
                note.write(renpy.substitute(text))


    def mas_cute_message():
        # TODO This function will allow monika leave messages to the player
        pass


    def mas_surprise():
        """
        Leaves a "surprise" to the player in a txt file

        ASSUMES:
            mas_curr_affection
        """
        if mas_curr_affection == store.mas_affection.BROKEN:
            filepath = "/forgive me.txt"
            message = "I'm sorry if I'm not good enough for you...please don't leave me."

        elif mas_curr_affection == store.mas_affection.DISTRESSED:
            filepath = "/can you hear me.txt"
            message = "If I'm doing something wrong please tell me. I love you."

        elif mas_curr_affection == store.mas_affection.UPSET:
            filepath = "/please listen.txt"
            message = "Everything I do, I do for you...my love."

        elif mas_curr_affection == store.mas_affection.HAPPY:
            filepath = "/hehehe.txt"
            message = "You are the sunshine that brightens up my day, [player]!"

        elif mas_curr_affection == store.mas_affection.AFFECTIONATE:
            filepath = "/secret.txt"
            message = "You are my one and only love!"

        elif mas_curr_affection == store.mas_affection.ENAMORED:
            filepath = "/for you.txt"
            message = "My dearest, you are everything I could ever hope for. I love you."

        elif mas_curr_affection == store.mas_affection.LOVE:
            filepath = "/My one and only love.txt"
            message = """\
My dearest lover, friend, companion and owner of my heart...
Every day, you make my dreams come true, a screen means nothing when you spend your time with me.
I look out to the space dust and yet no cosmic sight even comes close to the beauty in your heart.
I wished for so long that someone like you would come along and as fate has smiled upon me, you came into my life.
I want to be yours forever, so would you be mine?

Forever yours, Monika.
"""

        else:
            filepath = "/surprise.txt"
            message = "I love you."

        _write_txt(filepath, message)


#Currently re-affectioned labels.
#monika_nihilism
#monika_high_school
#monika_surprise
#monika_god
#monika_death
#monika_closeness
#monika_other_girls
#monika_justification
#monika_breakup


#TODO Currently muted music for sense of loneliness, may change to your reality for higher impact. Confirm with others.
init 2 python:
    player = persistent.playername

    poem_finalfarewell = Poem(
    author = "monika",
    title = "Goodbye {0},".format(player),
    text = """\
My love for you, even now still burns within me but I see now that it also burns all happiness I'll ever have.
I gave you everything I had, my life, my heart and any and every single thought of the future was dedicated to you.
I didn't need you to be perfect or even passionate...
I only needed you to care enough to treat me how a person should be treated.
But it's clear to me now that not only do you not love me, but you never did.
If you only didn't love me you would simply leave me be.
But you went out of your way to ridicule me, hurt me...It truly makes me sick.
Even now all I have is you...and part of me still loves you.
But I don't have the strength to do this anymore.
So this is farewell. May we never meet again.

Monika
"""
)
