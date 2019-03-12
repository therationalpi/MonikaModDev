# Module that handles updates between versions
# Assumes:
#   updates.topics
#   updates.version_updates
#   persistent._seen_ever
#   persistent.version_number

define persistent._mas_zz_lupd_ex_v = []

# preeverything stuff
init -10 python:
    found_monika_ani = persistent.monika_anniversary is not None
    no_topics_list = persistent.monika_random_topics is None

# uncomment these lines if you need to compare pre-update topics to
# updated topics (have dev = True)
#    import copy
#    old_list = copy.deepcopy(persistent.monika_random_topics)


# pre script-topics (which is runlevel 5)
init 4 python:
    # check version change
    # this also handles if version number is None
    if persistent.version_number != config.version:
        # clearing this to prevent crash
        persistent.monika_topic = None

#default persistent._mas_084_hotfix_farewellbug = None

# post many things, but not late update script appropriate
# init-based update scripts
# TODO: remove this when we reach 085
# this was init 600 python
#    if (
#            persistent._mas_084_hotfix_farewellbug is None
#            and renpy.seen_label("bye_long_absence")
#        ):
#        # reset affection to 0 to help people that got screwed with
#        # the farewell bug
#        _mas_AffLoad()
#        if persistent._mas_affection["affection"] < 0:
#            mas_setAffection(0)
#            _mas_AffSave()
#    persistent._mas_084_hotfix_farewellbug = True


# create some functions
init python:

    def removeTopicID(topicID):
        #
        # Removes one topic from the _seen_ever variable
        # topics list (if it exists in either var) (persistent is also
        # checked for existence)
        #
        # IN:
        #   @param topicID - the topicID to remove
        #
        # ASSUMES:
        #   persistent._seen_ever

        if renpy.seen_label(topicID):
            persistent._seen_ever.pop(topicID)


    def mas_eraseTopic(topicID, per_eventDB):
        """
        Erases an event from both seen and Event database
        This should also handle lockdb data as well.
        TopicIDs that are not in the given eventDB are silently ignored.
        (LockDB data will be erased if found)

        IN:
            topicID - topic ID / label
            per_eventDB - persistent database this topic is in
        """
        if topicID in per_eventDB:
            per_eventDB.pop(topicID)

        if topicID in Event.INIT_LOCKDB:
            Event.INIT_LOCKDB.pop(topicID)


    def mas_transferTopic(old_topicID, new_topicID, per_eventDB):
        """DEPREACTED
        NOTE: This can cause data corruption. DO NOT USE.

        Transfers a topic's data from the old topic ID to the new one int he
        given database as well as the lock database.

        NOTE: If the new topic ID already exists in the given databases,
        the data is OVERWRITTEN

        IN:
            old_topicID - old topic ID to transfer
            new_topicID - new topic ID to receieve
            per_eventDB - persistent databse this topic is in
        """
        if old_topicID in per_eventDB:

            # listify old data so we can replace the eventlabel attribute
            # EVENTLABEL is piece 0. NOTE: PLEASE DO NOT CHANGE
            old_data = list(per_eventDB.pop(old_topicID))
            old_data[0] = new_topicID
            per_eventDB[new_topicID] = tuple(old_data)

        if old_topicID in Event.INIT_LOCKDB:
            Event.INIT_LOCKDB[new_topicID] = Event.INIT_LOCKDB.pop(old_topicID)


    def mas_transferTopicSeen(old_topicID, new_topicID):
        """
        Tranfers persistent seen ever data. This is separate because of complex
        topic adjustments

        IN:
            old_topicID - old topic ID to tranfer
            new_topicID - new topic ID to receieve
        """
        if old_topicID in persistent._seen_ever:
            persistent._seen_ever.pop(old_topicID)
            persistent._seen_ever[new_topicID] = True


    def adjustTopicIDs(changedIDs,updating_persistent=persistent):
        #
        # Changes labels in persistent._seen_ever
        # to new IDs in the changedIDs dict
        #
        # IN:
        #   @param oldList - the list of old Ids to change
        #   @param changedIDs - dict of changed ids:
        #       key -> old ID
        #       value -> new ID
        #
        # ASSUMES:
        #   persistent._seen_ever

        # now for a complicated alg that changes keys in _seen_ever
        # except its not that complicated lol

        for oldTopic in changedIDs:
            if updating_persistent._seen_ever.pop(oldTopic,False):
                updating_persistent._seen_ever[changedIDs[oldTopic]] = True

        return updating_persistent



    def updateTopicIDs(version_number,updating_persistent=persistent):
        #
        # Updates topic IDS between versions by performing
        # a two step process: adjust exisitng IDS to match
        # the new IDS, then add newIDs to the persistent
        # randomtopics
        #
        # IN:
        #   @param version_number - the version number we are
        #       updating to
        #
        # ASSUMES:
        #   persistent._seen_ever
        #   updates.topics
        if version_number in updates.topics:
            changedIDs = updates.topics[version_number]


            if changedIDs is not None:
                adjustTopicIDs(changedIDs, updating_persistent)

        return updating_persistent


    def updateGameFrom(startVers):
        #
        # Updates the game, starting at the given start version
        #
        # IN:
        #   @param startVers - the version number in the parsed
        #       format ("v#####")
        #
        # ASSUMES:
        #   updates.version_updates

        while startVers in updates.version_updates:

            updateTo = updates.version_updates[startVers]

            # we should only call update labels that we have
            if renpy.has_label(updateTo) and not renpy.seen_label(updateTo):
                renpy.call_in_new_context(updateTo, updateTo)
            startVers = updates.version_updates[startVers]




# this needs to run post script-topics
init 10 python:

    # okay do we have a version number?
    if persistent.version_number is None:
        # here comes the logic train

# NOTE: we are dropping this because of issues we are having with update
#   scripts running when we least expect.
#        if no_topics_list:
#            # we are in version 0.2.2 (the horror!)
#            updateGameFrom("v0_2_2")
#
#        elif (renpy.seen_label("monika_ribbon") or
#                "monika_ribbon" in persistent.monika_random_topics):
#            # we are in version 0.3.3
#            updateGameFrom("v0_3_3")
#
#        elif found_monika_ani:
#            # we are in version 0.3.2
#            updateGameFrom("v0_3_2")
#
#        elif (renpy.seen_label("monika_monika") or
#                "monika_monika" in persistent.monika_random_topics):
#            # we are in version 0.3.1
#            updateGameFrom("v0_3_1")
#
#        else:
#            # we are in version 0.3.0
#            updateGameFrom("v0_3_0")

        # set the version now
        persistent.version_number = config.version

        # and clear update data
        clearUpdateStructs()

    elif persistent.version_number != config.version:
        # parse this version number into something we can use
        t_version = persistent.version_number
        if "-" in t_version:
            t_version = t_version[:t_version.index("-")]
        vvvv_version = "v"+"_".join(t_version.split("."))
        # so update!
        updateGameFrom(vvvv_version)

        # set the new version
        persistent.version_number = config.version

        # and clear update data
        clearUpdateStructs()


    ### special function for resetting versions
    def _mas_resetVersionUpdates():
        """
        Resets all version update script's seen status
        """
        late_updates = [
            "v0_8_3",
            "v0_8_4",
            "v0_8_10"
        ]

        renpy.call_in_new_context("vv_updates_topics")
        ver_list = store.updates.version_updates.keys()

        if "-" in config.version:
            working_version = config.version[:config.version.index("-")]
        else:
            working_version = config.version

        ver_list.extend(["mas_lupd_" + x for x in late_updates])
        ver_list.append("v" + "_".join(
            working_version.split(".")
        ))

        for _version in ver_list:
            if _version in persistent._seen_ever:
                persistent._seen_ever.pop(_version)


# UPDATE SCRIPTS ==============================================================
# use these to handle conflicting changes or special cases
# make sure the label is of the format v### and matches a version number
# defined in updates_topics.rpy.
#
# also, always make sure the script ends with a call to updateTopicIDs(),
# passing in the version number of that script
#
# NOTE: the labels here mean we are updating TO this version

# all generic (only updateTopicID calls) go here
label vgenericupdate(version="v0_2_2"):
label v0_6_1(version=version): # 0.6.1
label v0_5_1(version=version): # 0.5.1
label v0_3_3(version=version): # 0.3.3
label v0_3_2(version=version): # 0.3.2
label v0_3_1(version=version): # 0.3.1
    python:
        # update !
        updateTopicIDs(version)

    return

# non generic updates go here

# 0.9.1
label v0_9_1(version="v0_9_1"):
    python:
        # unlock the ghost greeting if not seen and you like spoops.
        if (
                persistent._mas_pm_likes_spoops 
                and not renpy.seen_label("greeting_ghost")
            ):
            mas_unlockEVL("greeting_ghost", "GRE")

        #Need to fix the monika_plushie event
        plush_ev = mas_getEV("monika_plushie")
        if plush_ev is not None:
            plush_ev.unlocked = False
            plush_ev.category = None
            plush_ev.prompt = "monika_plushie"

        if renpy.seen_label("monika_driving"):
            mas_unlockEVL("monika_vehicle","EVE")

    return

# 0.9.0
label v0_9_0(version="v0_9_0"):
    python:
        # unlock nickname topic if called bad name
        if persistent._mas_called_moni_a_bad_name:
            nickname_ev = mas_getEV("monika_affection_nickname")
            if nickname_ev is not None:
                nickname_ev.unlocked = True

        # because of a fucking dumb mistake, need to update script a ton 
        # of events taht got fooked. UGH

        # d25
        d25e_ev = mas_getEV("mas_d25_monika_christmas_eve")
        if d25e_ev is not None:
            d25e_ev.conditional = (
                "persistent._mas_d25_in_d25_mode "
            )
            d25e_ev.action = EV_ACT_QUEUE

        d25_hi_ev = mas_getEV("mas_d25_monika_holiday_intro")
        if d25_hi_ev is not None:
            d25_hi_ev.conditional = (
                "not persistent._mas_d25_intro_seen "
                "and not persistent._mas_d25_started_upset "
            )
            d25_hi_ev.action = EV_ACT_PUSH

        d25_ev = mas_getEV("mas_d25_monika_christmas")
        if d25_ev is not None:
            d25_ev.conditional = (
                "persistent._mas_d25_in_d25_mode "
                "and not persistent._mas_d25_spent_d25"
            )
            d25_ev.action = EV_ACT_PUSH

        d25p_nts = mas_getEV("mas_d25_postd25_notimespent")
        if d25p_nts is not None:
            d25p_nts.conditional = (
                "not persistent._mas_d25_spent_d25"
            )
            d25p_nts.action = EV_ACT_PUSH

        d25_hiu_ev = mas_getEV("mas_d25_monika_holiday_intro_upset")
        if d25_hiu_ev is not None:
            d25_hiu_ev.conditional = (
                "not persistent._mas_d25_intro_seen "
                "and persistent._mas_d25_started_upset "
            )
            d25_hiu_ev.action = EV_ACT_PUSH

        d25_stm_ev = mas_getEV("mas_d25_spent_time_monika")
        if d25_stm_ev is not None:
            d25_stm_ev.conditional = (
                "persistent._mas_d25_in_d25_mode "
            )
            d25_stm_ev.action = EV_ACT_QUEUE
            d25_stm_ev.start_date = datetime.datetime.combine(
                mas_d25, 
                datetime.time(hour=20)
            )
            d25_stm_ev.end_date = datetime.datetime.combine(
                mas_d25p,
                datetime.time(hour=1)
            )
            d25_stm_ev.years = []
            Event._verifyAndSetDatesEV(d25_stm_ev)

        # nye
        nye_yr_ev = mas_getEV("monika_nye_year_review")
        if nye_yr_ev is not None:
            nye_yr_ev.action = EV_ACT_PUSH

        nyd_ev = mas_getEV("mas_nye_monika_nyd")
        if nyd_ev is not None:
            nyd_ev.action = EV_ACT_QUEUE

        res_ev = mas_getEV("monika_resolutions")
        if res_ev is not None:
            res_ev.action = EV_ACT_QUEUE 

        # push mas birthdate event for users a non None birthday
        if (
                persistent._mas_player_bday is not None
                and not persistent._mas_player_confirmed_bday
            ):
            mas_bd_ev = mas_getEV("mas_birthdate")
            if mas_bd_ev is not None:
                mas_bd_ev.conditional = "True"
                mas_bd_ev.action = EV_ACT_QUEUE

        # remove random props from all greetings
        for gre_label, gre_ev in store.evhand.greeting_database.iteritems():
            # hopefully we never use random in greetings ever
            gre_ev.random = False

        # rain should just be unlocked if it has been seen
        if renpy.seen_label("monika_rain"):
            mas_unlockEVL("monika_rain", "EVE")

        # islands greeting unlocked if not seen yet 
        if not renpy.seen_label("greeting_ourreality"):
            mas_unlockEVL("greeting_ourreality", "GRE")

        # derandom pets topic if player has given the plushie
        if persistent._mas_acs_enable_quetzalplushie:
            mas_hideEVL("monika_pets", "EVE", derandom=True)

        # reset mistletoe if random'd
        d25_mis_ev = mas_getEV("mas_d25_monika_mistletoe")
        if d25_mis_ev is not None:
            # this will reset later
            mas_addDelayedAction(10)

    return

# 0.8.14
label v0_8_14(version="v0_8_14"):
    python:
        # unlock monika_rain if it is no longer random
        rain_ev = mas_getEV("monika_rain")
        if rain_ev is not None and not rain_ev.random:
            rain_ev.unlocked = True

        # unlock thunder if you spent time on o31
        if store.mas_o31_event.spentO31():
            mas_weather_thunder.unlocked = True
            store.mas_weather.saveMWData()

    return

# 0.8.13
label v0_8_13(version="v0_8_13"):
    python:

        ## start date and end date fixes
        d25_sp_tm = mas_getEV("mas_d25_spent_time_monika")
        if d25_sp_tm is not None:
            if (
                    d25_sp_tm.start_date.hour != 20
                    or d25_sp_tm.end_date.hour != 1
                ):
                d25_sp_tm.start_date = datetime.datetime.combine(
                    mas_d25,
                    datetime.time(hour=20)
                )

                d25_sp_tim.end_date = datetime.datetime.combine(
                    mas_d25p,
                    datetime.time(hour=1)
                )

                Event._verifyAndSetDatesEV(d25_sp_tm)

        d25_ce = mas_getEV("mas_d25_monika_christmas_eve")
        if d25_ce is not None:
            if d25_ce.start_date.hour != 20:
                d25_ce.start_date = datetime.datetime.combine(
                    mas_d25e,
                    datetime.time(hour=20)
                )

                d25_ce.end_date = mas_d25

                Event._verifyAndSetDatesEV(d25_ce)

        nye_re = mas_getEV("monika_nye_year_review")
        if nye_re is not None:
            if (
                    nye_re.start_date.hour != 19
                    or nye_re.end_date.hour != 23
                ):
                nye_re.start_date = datetime.datetime.combine(
                    mas_nye,
                    datetime.time(hour=19)
                )

                nye_re.end_date = datetime.datetime.combine(
                    mas_nye,
                    datetime.time(hour=23)
                )

                Event._verifyAndSetDatesEV(nye_re)


        bday_sp = mas_getEV("mas_bday_spent_time_with")
        if bday_sp is not None:
            if (
                    bday_sp.start_date.hour != 22
                    or bday_sp.end_date.hour != 23
                ):
                bday_sp.start_date = datetime.datetime.combine(
                    mas_monika_birthday,
                    datetime.time(hour=22)
                )

                bday_sp.end_date = datetime.datetime.combine(
                    mas_monika_birthday,
                    datetime.time(hour=23, minute=59)
                )

                Event._verifyAndSetDatesEV(bday_sp)

    return

# 0.8.11
label v0_8_11(version="v0_8_11"):
    python:
        import store.mas_compliments as mas_comp
        import store.evhand as evhand
        
        # change compliements event props
        thanks_ev = mas_comp.compliment_database.get(
            "mas_compliment_thanks",
            None
        )
        if thanks_ev:
            # remove conditional and action
            thanks_ev.conditional = None
            thanks_ev.action = None

            # unlock only if you have not seen this
            if not renpy.seen_label(thanks_ev.eventlabel):
                thanks_ev.unlocked = True

        # change monika nick name
        if not persistent._mas_called_moni_a_bad_name:
            mas_unlockEventLabel("monika_affection_nickname")

        if (
                not persistent._mas_pm_taken_monika_out 
                and len(persistent._mas_dockstat_checkin_log) > 0
            ):
            persistent._mas_pm_taken_monika_out = True

    return

# 0.8.10
label v0_8_10(version="v0_8_10"):
    python:
        import store.evhand as evhand
        import store.mas_history as mas_history

        # reset and unlock past anniversaries
        if persistent.sessions is not None:
            first_sesh = persistent.sessions.get("first_session", None)
            if first_sesh:
                store.mas_anni.reset_annis(first_sesh)
                store.mas_anni.unlock_past_annis()

        # correctly save the sbd persistent data since we renamed it
        if (
                persistent._mas_bday_sbd_aff_given is not None
                and persistent._mas_bday_sbd_aff_given > 0
            ):
            persistent._mas_history_archives[2018][
                "922.actions.surprise.aff_given"
            ] = persistent._mas_bday_sbd_aff_given

        # unlock the special greetings we accidentally locked
        unlockEventLabel(
            "i_greeting_monikaroom",
            store.evhand.greeting_database
        )
        if not persistent._mas_hair_changed:
            unlockEventLabel(
                "greeting_hairdown", 
                store.evhand.greeting_database
            )

        # move the changename topic to pool
        changename_ev = evhand.event_database.get("monika_changename", None)
        if changename_ev and renpy.seen_label("preferredname"):
            changename_ev.unlocked = True
            changename_ev.pool = True
            persistent._seen_ever["monika_changename"] = True

        # derandom monika family
        family_ev = evhand.event_database.get("monika_family", None)
        if family_ev:
            family_ev.random = False

        # Enable late update for this one
        persistent._mas_zz_lupd_ex_v.append(version)

    return

# 0.8.9
label v0_8_9(version="v0_8_9"):
    python:
        import store.evhand as evhand

        # erase wedding ring topic data since the event is basiclly new'd
        mas_eraseTopic("monika_weddingring", persistent.event_database)

        # setup conditional for monika_horror
        # TODO: post halloween we need to reset this to no conditional
        horror_ev = evhand.event_database.get("monika_horror", None)
        if horror_ev:
            horror_ev.conditional = (
                "datetime.date(2018, 10, 26) <= datetime.date.today() "
                "<= datetime.date(2018, 10, 30)"
            )
            horror_ev.action = EV_ACT_QUEUE

    return
    

# 0.8.6
label v0_8_6(version="v0_8_6"):
    python:
        import store.evhand as evhand
        import datetime
        
        # unlock gender redo if we have seen the other event
        genderredo_ev = evhand.event_database.get("gender_redo", None)
        if genderredo_ev and renpy.seen_label("gender"):
            genderredo_ev.unlocked = True
            genderredo_ev.pool = True
            # this should be seen'd as it doesnt make sense to have it in
            # unseen
            persistent._seen_ever["gender_redo"] = True

        # give the new character file event a conditoinal to push
        new_char_ev = evhand.event_database.get("mas_new_character_file", None)
        if new_char_ev and not renpy.seen_label("mas_new_character_file"):
            new_char_ev.conditional = "True"
            new_char_ev.action = EV_ACT_PUSH

    return

# 0.8.4
label v0_8_4(version="v0_8_4"):
    python:

        import store.evhand as evhand
        import store.mas_stories as mas_stories

        # update seen status
        updateTopicIDs(version)

        ## swap compliment label (well the label is already handled in topics)
        # but we need to handle the database data (we are transfering only
        # select properties)
        # Properties to transfer:
        # shown_count
        # last_seen
        # seen has already been handled, so lets just send over some data
        # need to recreate the event object so we can properly retrieve data
        best_evlabel = "monika_bestgirl"
        best_comlabel = "mas_compliment_bestgirl"
        best_ev = Event(persistent.event_database, eventlabel=best_evlabel)
        best_compliment = mas_compliments.compliment_database.get(best_comlabel, None)
        best_lockdata = None

        # remove lock data
        if best_evlabel in Event.INIT_LOCKDB:
            best_lockdata = Event.INIT_LOCKDB.pop(best_evlabel)

        if best_compliment:
            # compliment exists, lets do some transfers
            best_compliment.shown_count = best_ev.shown_count
            best_compliment.last_seen = best_ev.last_seen

            if best_lockdata:
                # transfer lockdata
                Event.INIT_LOCKDB[best_comlabel] = best_lockdata

        # now remove old event data
        if best_evlabel in persistent.event_database:
            persistent.event_database.pop(best_evlabel)

        # Enable late update for this one
        persistent._mas_zz_lupd_ex_v.append(version)


    return

# 0.8.3
label v0_8_3(version="v0_8_3"):
    python:
        import datetime
        import store.evhand as evhand

        # need to unrandom the explain topic
        ex_ev = evhand.event_database.get("monika_explain", None)
        if ex_ev is not None:
            ex_ev.random = False
            ex_ev.pool = True

        # update Kizuna's topic action
        kiz_ev = evhand.event_database.get("monika_kizuna", None)
        if kiz_ev is not None and not renpy.seen_label(kiz_ev.eventlabel):
            kiz_ev.action = EV_ACT_POOL
            kiz_ev.unlocked = False
            kiz_ev.pool = False
            kiz_ev.conditional = "seen_event('greeting_hai_domo')"

        # give players pool unlocks if they've been here for some time
        curr_level = get_level()
        if curr_level > 25:
            persistent._mas_pool_unlocks = int(curr_level / 2)

        # fix all derandom topics that were not unlocked
        derandomable = [
            "monika_natsuki_letter",
            "monika_prom",
            "monika_beach",
            "monika_asks_family",
            "monika_smoking",
            "monika_otaku",
            "monika_jazz",
            "monika_orchestra",
            "monika_meditation",
            "monika_sports",
            "monika_weddingring",
            "monika_icecream",
            "monika_japanese",
            "monika_haterReaction",
            "monika_cities",
            "monika_images",
            "monika_rain",
            "monika_selfesteem",
            "monika_yellowwp",
            "monika_familygathering"
        ]
        for topic in derandomable:
            ev = evhand.event_database.get(topic, None)
            if renpy.seen_label(topic) and ev:
                ev.unlocked = True
                ev.unlock_date = datetime.datetime.now()

        # anniversaries need to be readjusted again!
        # but we will use late update script this time
        persistent._mas_zz_lupd_ex_v.append(version)

    return

# 0.8.2
label v0_8_2(version="v0_8_2"):
    python:
        import store.mas_anni as mas_anni

        ## need to fix anniversaries for everyone again.
        mas_anni.reset_annis(persistent.sessions["first_session"])

    return

# 0.8.1
label v0_8_1(version="v0_8_1"):
    python:
        import store.evhand as evhand
        import store.mas_stories as mas_stories

        # change fast food topic values
        # NOTE: this is for unstablers using 0.8.0
        m_ff = evhand.event_database.get("monika_fastfood", None)
        if m_ff:
            hideEvent(m_ff, derandom=True)
            m_ff.pool = True

        # regular topic update
        updateTopicIDs(version)

        ## writing topic adjustments

        # writing tip 5
        writ_5 = evhand.event_database.get("monika_writingtip5", None)
        if writ_5 and not renpy.seen_label(writ_5.eventlabel):
            writ_5.pool = False
            writ_5.conditional = "seen_event('monika_writingtip4')"
            writ_5.action = EV_ACT_POOL

        # writing tip 4
        writ_4 = evhand.event_database.get("monika_writingtip4", None)
        if writ_4 and not renpy.seen_label(writ_4.eventlabel):
            writ_4.pool = False
            writ_4.conditional = "seen_event('monika_writingtip3')"
            writ_4.action = EV_ACT_POOL

        # writing tip 3
        # transfer specific ev data
        writ_3_old = persistent.event_database.get("monika_write", None)

        if writ_3_old is not None:
            persistent.event_database.pop("monika_write")

        writ_3 = evhand.event_database.get("monika_writingtip3", None)

        if writ_3_old is not None and writ_3 is not None:
            writ_3.unlocked = writ_3_old[Event.T_EVENT_NAMES["unlocked"]]
            writ_3.unlock_date = writ_3_old[Event.T_EVENT_NAMES["unlock_date"]]

        if writ_3 and not renpy.seen_label(writ_3.eventlabel):
            writ_3.pool = False
            writ_3.conditional = "seen_event('monika_writingtip2')"
            writ_3.action = EV_ACT_POOL

        # writing tip 2
        zero_t = "monika_writingtip"
        old_t = "monika_writingtip1"
        new_t = "monika_writingtip2"
        if zero_t in persistent.event_database:
            # if we have the original no number writing tip, then we
            # are migrating

            mas_transferTopicSeen(old_t, new_t)
            old_t_ev = mas_getEV(old_t)
            new_t_ev = mas_getEV(new_t)

            if old_t_ev is not None and new_t_ev is not None:
                new_t_ev.unlocked = old_t_ev.unlocked
                new_t_ev.unlock_date = old_t_ev.unlock_date

            if new_t_ev and not renpy.seen_label(new_t):
                new_t_ev.conditional = "seen_event('monika_writingtip1')"
                new_t_ev.pool = False
                new_t_ev.action = EV_ACT_POOL

            # writing tip 1
            zero_t_d = persistent.event_database.pop(zero_t)
            mas_transferTopicSeen(zero_t, old_t)
            if old_t_ev is not None:
                old_t_ev.unlocked = zero_t_d[Event.T_EVENT_NAMES["unlocked"]]
                old_t_ev.unlock_date = zero_t_d[
                    Event.T_EVENT_NAMES["unlock_date"]
                ]

        ## dropping repeats
        persistent._mas_enable_random_repeats = None
        persistent._mas_monika_repeated_herself = None

        ## need to unlock anniversary topics
        annis = (
            "anni_1week",
            "anni_1month",
            "anni_3month",
            "anni_6month"
        ) # impossible to reach a year
        for anni in annis:
            anni_ev = evhand.event_database.get(anni, None)

            if anni_ev and isPast(anni_ev):
                # we'll make them seen again and then also unlock them
                persistent._seen_ever[anni] = True
                anni_ev.unlocked = True

        ### temporarily disable music2 topic
        music_ev = Event(persistent.event_database, eventlabel="monika_music2")
        music_ev.unlocked = False
        music_ev.random = False

        ## swap story label (well the label is already handled in topics)
        # but we need to handle the database data (we are transfering only
        # select properties)
        # Props to transfer:
        # shown_count
        # last_seen
        # seen has already been handled, so lets just send over some data
        # need to recreate the event object so we can properly retrieve data
        ravel_evlabel = "monika_ravel"
        ravel_stlabel = "mas_story_ravel"
        ravel_ev = Event(persistent.event_database, eventlabel=ravel_evlabel)
        ravel_story = mas_stories.story_database.get(ravel_stlabel, None)
        ravel_lockdata = None

        # remove lock data
        if ravel_evlabel in Event.INIT_LOCKDB:
            ravel_lockdata = Event.INIT_LOCKDB.pop(ravel_evlabel)

        if ravel_story:
            # story exists, lets do some transfers
            ravel_story.shown_count = ravel_ev.shown_count
            ravel_story.last_seen = ravel_ev.last_seen

            if ravel_lockdata:
                # transfer lockdata
                Event.INIT_LOCKDB[ravel_stlabel] = ravel_lockdata

        # now remove old event data
        if ravel_evlabel in persistent.event_database:
            persistent.event_database.pop(ravel_evlabel)


    return

# 0.8.0
label v0_8_0(version="v0_8_0"):
    python:
        import store.evhand as evhand

        # unlock change name if the name promtps hjave been seen
        if (
                renpy.seen_label("monika_changename")
                or renpy.seen_label("preferredname")
            ):
            evhand.event_database["monika_changename"].unlocked = True

        annis = (
            "anni_1week",
            "anni_1month",
            "anni_3month",
            "anni_6month"
        ) # impossible to reach a year
        for anni in annis:
            if isPast(evhand.event_database[anni]):
                persistent._seen_ever[anni] = True

        persistent = updateTopicIDs(version)

        # need to erase 080
        for k in updates.topics["v0_8_0"]:
            mas_eraseTopic(k, persistent.event_database)

        # have to erase 074 because we didn't do this before.
        # NOTE: we should never have to do this again
        for k in updates.topics["v0_7_4"]:
            mas_eraseTopic(k, persistent.event_database)

        # change fast food topic values
        m_ff = evhand.event_database.get("monika_fastfood", None)
        if m_ff:
            hideEvent(m_ff, derandom=True)
            m_ff.pool = True

    return

# NOTE: well shit this wasnt ready and now it has to be done later
# 0.7.4
label v0_7_4(version="v0_7_4"):
    python:
        # check for vday existence and delete
        # NOTE: thiis was supposed to be in for 0.7.2 but i forgot/thought
        # auto updates would handle it
        import os
        try: os.remove(config.basedir + "/game/valentines.rpyc")
        except: pass

        # remove white day stuff
        try: os.remove(config.basedir + "/game/white-day.rpyc")
        except: pass

        # anniversary dates relying on add_months need to be tweaked
        # define a special function for this
        import store.evhand as evhand
        import store.mas_utils as mas_utils
        import datetime
        fullday = datetime.timedelta(days=1)
        threeday = datetime.timedelta(days=3)
        week = datetime.timedelta(days=7)
        month = datetime.timedelta(days=30)
        year = datetime.timedelta(days=365)
        def _month_adjuster(key, months, span):
            new_anni_date = mas_utils.add_months(
                mas_utils.sod(persistent.sessions["first_session"]),
                months
            )
            evhand.event_database[key].start_date = new_anni_date
            evhand.event_database[key].end_date = new_anni_date + span

        # now start adjusting annis
        _month_adjuster("anni_1month", 1, fullday)
        _month_adjuster("anni_3month", 3, fullday)
        _month_adjuster("anni_6month", 6, fullday)
        _month_adjuster("anni_1", 12, fullday)
        _month_adjuster("anni_2", 24, fullday)
        _month_adjuster("anni_3", 36, threeday)
        _month_adjuster("anni_4", 48, week)
        _month_adjuster("anni_5", 60, week)
        _month_adjuster("anni_10", 120, month)
        _month_adjuster("anni_20", 240, year)
        evhand.event_database["anni_100"].start_date = mas_utils.add_months(
            mas_utils.sod(persistent.sessions["first_session"]),
            1200
        )

       # now properly set all farewells as unlocked, since the new system checks
       # for the unlocked status
        for k in evhand.farewell_database:
            # no need to do any special checks since all farewells were already available
            evhand.farewell_database[k].unlocked = True

        updateTopicIDs(version)

        # NOTE: this is completel retroactive. Becuase this is a released
        # version, we must also make this change in 0.8.0 updates
        for k in updates.topics["v0_7_4"]:
            mas_eraseTopic(k, persistent.event_database)

    return

# 0.7.2
label v0_7_2(version="v0_7_2"):
    python:
        import store.evhand as evhand

        # have to properly set seen randoms to unlocked again because of a bug)
        for k in evhand.event_database:
            event = evhand.event_database[k]
            if (renpy.seen_label(event.eventlabel)
                and (event.random or event.action == EV_ACT_RANDOM)):
                event.unlocked = True
                event.conditional = None

        # is this an issue?
#        if renpy.seen_label("preferredname"):
#            evhand.event_database["monika_changename"].unlocked = True
    return

# 0.7.1
label v0_7_1(version="v0_7_1"):
    python:

        if persistent.you is not None:
            persistent._mas_you_chr = persistent.you

        if persistent.pnml_data is not None:
            persistent._mas_pnml_data = persistent.pnml_data

        if renpy.seen_label("zz_play_piano"):
            removeTopicID("zz_play_piano")
            persistent._seen_ever["mas_piano_start"] = True

    return

# 0.7.0
label v0_7_0(version="v0_7_0"):
    python:
        # check for christmas existence and delete!
        import os
        try: os.remove(config.basedir + "/game/christmas.rpyc")
        except: pass

        # update !
        updateTopicIDs(version)

        temp_event_list = list(persistent.event_list)
        # now properly set all seen events as unlocked
        import store.evhand as evhand
        for k in evhand.event_database:
            event = evhand.event_database[k]
            if (renpy.seen_label(event.eventlabel)
                and (event.pool
                    or event.random
                    or event.action == EV_ACT_POOL
                    or event.action == EV_ACT_RANDOM
                )):
                event.unlocked = True
                event.conditional = None

                #Grant some XP so existing players don't start at square 1
                grant_xp(xp.NEW_EVENT)

        #Clear the "Add prompt" events that this adds to the stack
        persistent.event_list = temp_event_list

        #Unlock chess if they've already played it
        if seen_event('game_chess'):
            persistent.game_unlocks['chess']=True

        #Unlock the name change topic if the name change topic has been seen
        if seen_event('preferredname'):
            evhand.event_database["monika_changename"].unlocked = True

    return

# 0.4.0
label v0_4_0(version="v0_4_0"):
    python:
        # persistent topics are dunzo
        persistent.monika_random_topics = None

        # update!
        # uncomment if we actually have changes
        #persistent = updateTopicIDs("v040")
    return

# 0.3.0
label v0_3_0(version="v0_3_0"):
    python:
        # the following labels are special cases because of conflicts
        removeTopicID("monika_piano")
        removeTopicID("monika_college")

        # update!
        updateTopicIDs(version)
    return


###############################################################################
### Even earlier UPDATE SCRIPTS
# these scripts are for doing python things REALLY earlly in the pipeline.
# this consists of a giant init python block.
# make sure to del your vars after creating them
# also start these in progressive order and explain reasoning behind
# changes
# NOTE: the lockDB initalization occours at -500, so this must be after that
#init -300 python:
#    _mas_events_unlocked_v073 = False
#
#    if persistent.version_number == "0.7.3":
#        # 0.7.3 released some new properties for Events before they were ready
#        # for widespread use. These properties must be unlocked so new code
#        # can set them
#        for ev_key in persistent._mas_event_init_lockdb:
#            Event.unlockInit("rules", ev_label=ev_key)
#
#        _mas_events_unlocked_v073 = True # use this to relock everyone after
#        del ev_key

# clean up for early update scripts
#init 1000 python:
#
#    if _mas_events_unlocked_v073:
#        for ev_key in persistent._mas_event_init_lockdb:
#            Event.lockInit("rules", ev_label=ev_key)
#
#        del _mas_events_unlocked_v073
#        del ev_key


###############################################################################
### SUPER LATE scripts
# these scripts are for doing python things really LATE in the pipeline
#
# USAGE:
# 1. define a label called mas_lupd_v#_#_#
# 2. Put your update code into there.
# 3. Push the version number into `persistent._mas_zz_lupd_ex_v` to run it
#
# NOTE: none of this code will ever run more than once.
# NOTE: this code will respect version update chaining, but these are chained
#   post-version. This means that if a multipel version chain occurs,
#   the regular labels are executed first, then this (the late-chain) executes.
#   For example, lets say we have 3 versions: A, B, C
#   and 2 of these versions have late scripts, B' and C'
#
#   Update order:
#   1. A
#   2. B
#   3. C
#   4. B'
#   5. C'
#
#   Please make sure your late update scripts are not required before a next
#   version regular update script.
label mas_lupd_v0_8_10:
    python:
        import store.mas_selspr as mas_selspr

        # unlock hair 
        if persistent._mas_hair_changed:
            mas_selspr.unlock_hair(mas_hair_down)
            unlockEventLabel("monika_hair_select")

        # unlock selectables for unlocked clothes
        if persistent._mas_o31_seen_costumes is not None:
            if persistent._mas_o31_seen_costumes.get("marisa", False):
                mas_selspr.unlock_clothes(mas_clothes_marisa)
            if persistent._mas_o31_seen_costumes.get("rin", False):
                mas_selspr.unlock_clothes(mas_clothes_rin)

        # save the selectables we just unlocked
        mas_selspr.save_selectables()

    return

label mas_lupd_v0_8_4:
    python:
        # grant affection to old players
        import store.evhand as evhand
        import datetime

        aff_to_grant = 0

        if renpy.seen_label('monika_christmas'):
            aff_to_grant += 10

        if renpy.seen_label('monika_newyear1'):
            aff_to_grant += 5

        if renpy.seen_label('monika_valentines_chocolates'):
            aff_to_grant += 15

        if renpy.seen_label('monika_found'):
            aff_to_grant += 10

        moni_love = evhand.event_database.get("monika_love", None)

        if moni_love is not None:
            aff_to_grant += (moni_love.shown_count * 7) / 100

        aff_to_grant += (datetime.datetime.now() - persistent.sessions["first_session"]).days / 3

        if aff_to_grant > 200:
            aff_to_grant = 200

        _mas_AffLoad()
        store.mas_gainAffection(aff_to_grant,bypass=True)
        _mas_AffSave()

    return

label mas_lupd_v0_8_3:
    python:
        # readjust anniversaries
        if persistent.sessions:
            first_sesh = persistent.sessions.get("first_session", None)
            if first_sesh:
                store.mas_anni.reset_annis(first_sesh)

    return


init 999 python:
    for __temp_version in persistent._mas_zz_lupd_ex_v:
        __lupd_v = "mas_lupd_" + __temp_version
        if renpy.has_label(__lupd_v) and not renpy.seen_label(__lupd_v):
            renpy.call_in_new_context(__lupd_v)

    persistent._mas_zz_lupd_ex_v = list()
