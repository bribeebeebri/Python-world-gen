# -*- coding: utf-8 -*-
"""
Created on Sat Dec 25 21:04:55 2021

@author: Bri
"""

import random
from src_tools import *
from src_events import *
import string

class Curse:
    def __init__(self,m,c,a):
        self.tt = "curse"
        self.magic = m
        self.myMap = self.magic.myMap
        self.myMap.curses.append(self)
        self.caster = c
        self.strength = a
        curseTypes = ["decay","hatred","sloth","stupidity"]
        self.kind = random.choice(curseTypes)
        self.cursedEntities = []
        self.length = random.random()
        self.length = self.length**2
        self.length = math.ceil(self.strength*self.strength*50) + math.ceil(self.length*50)
        self.age = 0
    def curseEntity(self,t):
        if t not in self.cursedEntities:
            self.cursedEntities.append(t)
    def spread(self):
        if self.magic.target == "bloodline":
            for n in self.cursedEntities:
                if n.tt == "pop":
                    for i in n.parents:
                        if i not in self.cursedEntities:
                            self.curseEntity(i)
                    for i in n.kids:
                        if i not in self.cursedEntities:
                            self.curseEntity(i)
    def decay(self,target):
        if target.tt == "pop":
            target.harmProportional(self.strength/7)
            for i in target.inventory:
                self.decay(i)
        if target.tt == "item":
            target.damage(self.strength/7)
        if target.tt == "node":
            harmMult = 1-(self.strength/10)
            target.permanentModifiers["rainfall"] *= harmMult
            target.permanentModifiers["carnivores"] *= harmMult
            target.permanentModifiers["herbivores"] *= harmMult
            target.permanentModifiers["vegetation"] *= harmMult
            target.permanentModifiers["fertility"] *= harmMult
            target.permanentModifiers["metallicity"] *= harmMult
            target.herbivores *= harmMult
            target.carnivores *= harmMult
            target.fertility *= harmMult
            target.metallicity *= harmMult
            for p in target.entities:
                self.decay(p)
    def hate(self,target):
        if target.tt == "pop":
            target.importance *= 1-(self.strength/10)
            if target.location != None:
                for e in target.location.entities:
                    if e != target:
                        e.dislike(target,self.strength/10)
                for e in target.relationships.values():
                    if e.location != target.location:
                        e.dislike(target,self.strength/10)
            for i in target.inventory:
                self.hate(i)
        if target.tt == "item":
            target.importance *= 1-(self.strength/8)
            if target.creator != None:
                target.creator.importance *= 1-(self.strength/24)
            if target.owner != None:
                target.owner.importance *= 1-(self.strength/16)
            if target.subect != None:
                target.subject.importance *= 1-(self.strength/50)
        if target.tt == "node":
            for p in target.entities:
                self.hate(p)
    def slow(self,target):
        if target.tt == "pop":
            target.speedModifier *= 1-(self.strength/6)
        if target.tt == "item":
            if target.owner != None:
                target.owner.speedModifier *= 1-(self.strength/6)
        if target.tt == "node":
            for p in target.entities:
                self.slow(p)
    def dull(self,target):
        if target.tt == "pop":
            target.skill *= 1-(self.strength/6)
        if target.tt == "item":
            target.quality *= 1-(self.strength/6)
        if target.tt == "node":
            for p in target.entities:
                self.dull(p)
    def updateCurse(self):
        self.age += 1
        if self.age >= self.length:
            return "Expired"
        self.spread()
        for e in self.cursedEntities:
            if self.kind == "decay":
                self.decay(e)
            if self.kind == "hatred":
                self.hate(e)
            if self.kind == "sloth":
                self.slow(e)
            if self.kind == "stupidity":
                self.dull(e)


class Magic:
    def __init__(self,c,n=False):
        self.tt = "magic"
        self.natural = n
        self.creator = c
        self.creator.magic.append(self)
        self.culture = self.creator.culture
        self.myMap = self.culture.myMap
        # Names
        prefixes = {"curse":["doom","curse","hate","hex","spite"],
                 "bless":["holy","sacrosanct","consecrating","purifying"],
                 "destroy":["deadly","death","inferno","fire","skull","mortal","horror","final","nightmare","doom","agony"],
                 "create":["genesis","primal","conjure","primordial"],
                 "transmute":["transmute","reshape","alchemical"],
                 "transport":["teleport","transport","translocate"],
                 "harm":["fire","vitriol","brimstone","meteor","pain","blood"],
                 "heal":["blessed","purification","mending","healing","light"],
                 "resurrect":["necromantic","soul","light","blessed","corpse","grave"],
                 "burn":["fire","brimstone","searing","combustion","inferno"],
                 "freeze":["ice","cold","arctic","biting","frost"],
                 "poison":["poison","toxic","noxious","caustic"]}
        suffixes = {"curse":["doom","curse","hate","hex","spite"],
                 "bless":["blessing","sanctity","beatitude","consecration","purification"],
                 "destroy":["death","fire","inferno","mortality","horror","finality","nightmare","doom","destruction"],
                 "create":["genesis","forge","creation","primality","molding","conjuration"],
                 "transmute":["transmutation","transformation","alchemy","recreation"],
                 "transport":["teleportation","translocation","transportation","flicker"],
                 "harm":["fire","vitriol","brimstone","meteor","pain","blood","blast"],
                 "heal":["blessing","purification","mending","healing","touch","light"],
                 "resurrect":["necromancy","revival","resurrection","unearthing","resuscitation","light"],
                 "burn":["torch","inferno","fire","brimstone","blast","pyre"],
                 "freeze":["chill","frost","icicle","blizzard","bite"],
                 "poison":["toxin","poison","infection","decay","miasma"]}
        # Choose a type of magic spell. This is (mostly?) cosmetic.
        kinds = ["incantation","meditation","spell","prayer","invocation","channeling","concoction","ritual","song","divination","sorcery"]
        naturalKinds = ["breath","song","roar","excretion","stare","bite"]
        # Choose one effect to do to the target; greater magnitudes are harder and less likely to be cast and generated
        effects = {"curse":-1.25,"bless":1,"destroy":-2.5,"create":3,"transmute":-0.6,"transport":-0.6,
                   "harm":-1.5,"heal":1,"resurrect":3,"burn":-1,"freeze":-1,"poison":-1.25}
        # Choose a target. Greater magnitudes are harder/less likely to be cast and generated
        targets = {"item":2,"person":3,"group":4,"bloodline":5,"location":6,"city":9,"region":15,"nation":26}
        naturalTargets = ["person","group","bloodline","location","city"]
        # These combinations of effects and targets won't be allowed.
        impossibleSpells = ["create region","create location",
                            "transport nation","transport region",
                            "transmute nation","transmute region","transmute location",
                            "transmute city"]
        self.kind = random.choice(kinds)
        if self.natural == True:
            self.kind = random.choice(naturalKinds)
        self.effect = random.choice(list(effects.keys()))
        self.target = random.choice(list(targets.keys()))
        while (self.effect + " " + self.target in impossibleSpells or abs(effects[self.effect]*targets[self.target]) > random.uniform(0,90)
        or (self.natural == True and self.target not in naturalTargets)):
            self.effect = random.choice(list(effects.keys()))
            self.target = random.choice(list(targets.keys()))
        self.strength = random.random()**2
        if self.natural == False:
            self.strength = self.strength*math.sqrt(self.culture.tech["magic"])
        self.strength = clamp((self.strength+self.creator.skill)/2,0.05,1)
        self.magnitude = effects[self.effect]*targets[self.target]
        s = self.culture.language.genName()
        roll = random.random()
        if roll < 0.25:
            s = s + " " + self.culture.language.genName()
        elif roll < 0.5 and len(suffixes[self.effect]) > 0:
            s = s + " " + random.choice(suffixes[self.effect])
        elif roll < 0.75 and len(prefixes[self.effect]) > 0:
            s = random.choice(prefixes[self.effect]) + " " + s
        else:
            s = s
        self.name = string.capwords(s)
        if self.natural == True:
            self.name = string.capwords(self.creator.justName() + "'s " + self.kind)
        self.culture.magic.append(self)
    def addBloodline(self,subjects,s):
        if s not in subjects:
            subjects.append(s)
            for q in s.parents:
                self.addBloodline(subjects,q)
            for q in s.kids:
                self.addBloodline(subjects,q)
        return subjects
    def cast(self,caster,subjects=[]):
        amount = clamp(self.strength*caster.skill,0.01,1)
        if self.target == "bloodline" and subjects != []:
            subjects = self.addBloodline(subjects,subjects[0])
        if self.target == "group" and subjects != []:
            for p in subjects[0].followers:
                subjects.append(p)
        obj=None
        for s in subjects:
            obj = self.apply(s,amount,caster,obj)
    def apply(self,subject,amount,caster,obj=None):
        harmMult = 1-amount
        helpMult = 1+amount
        roll = random.random()
        if subject.tt == "culture":
            targets = subject.cultureCities()
            targets = [c.node.resourceRegion for c in targets]
            for s in targets:
                obj = self.apply(s,amount,caster,obj)
        if subject.tt == "region" or subject.tt == "resourceRegion":
            for s in subject.nodes:
                obj = self.apply(s,amount,caster,obj)
        if subject.tt == "city":
            self.apply(subject.node,amount,caster,obj)
        if subject.tt == "org":
            for s in subject.members:
                obj = self.apply(s,amount,caster,obj)
        # Apply magic to ITEM -------------------------------------------------
        if subject.tt == "item":
            if subject.dead == 0:
                if self.effect == "bless":
                    if roll < amount:
                        subject.repair(1)
                if self.effect == "heal":
                    subject.repair(amount)
                if self.effect == "destroy":
                    if roll < amount:
                        subject.damage(1,[caster])
                if self.effect == ["harm","burn","freeze","poison"]:
                    subject.damage(amount,[caster])
            elif subject.dead == 1:
                if self.effect == "resurrect":
                    if roll < amount:
                        subject.restore()
            if self.effect == "curse":
                if roll < amount:
                    if obj == None:
                        obj = Curse(m=self,c=caster,a=amount)
                    obj.curseEntity(subject)
        # Apply magic to POP -------------------------------------------------
        if subject.tt == "pop":
            if subject.dead == 0:
                if self.effect == "bless":
                    if roll < amount:
                        subject.heal(1)
                if self.effect == "heal":
                    subject.heal(amount)
                if self.effect == "destroy":
                    if roll < amount:
                        subject.kill(1,[caster])
                if self.effect in ["harm","burn","freeze"]:
                    subject.harm(amount)
                if self.effect == "poison":
                    subject.harm(amount)
                    if obj == None and roll < amount:
                        obj = Illness(n=subject.location,p=[subject])
                        obj.infectivity = helpMult
                        obj.mortality = clamp(harmMult,0.1,0.9)
                        obj.length = math.ceil(amount*(9))
                        obj.name = self.name
                    elif obj != None and roll < amount:
                        obj.infect(subject)
            elif subject.dead == 1:
                if self.effect == "resurrect":
                    if roll < amount:
                       subject.resurrect()
            if self.effect == "curse":
                if roll < amount:
                    if obj == None:
                        obj = Curse(m=self,c=caster,a=amount)
                    obj.curseEntity(subject)
            for i in subject.inventory:
                    obj = self.apply(i,amount,caster,obj)          
        # Apply magic to NODE -------------------------------------------------
        if subject.tt == "node":
            if self.effect == "bless":
                helpMult = 1.3
                subject.permanentModifiers["rainfall"] = helpMult
                subject.permanentModifiers["carnivores"] = helpMult
                subject.permanentModifiers["herbivores"] = helpMult
                subject.permanentModifiers["vegetation"] = helpMult
                subject.permanentModifiers["fertility"] = helpMult
                subject.permanentModifiers["metallicity"] = helpMult
                subject.herbivores *= helpMult
                subject.carnivores *= helpMult
                subject.fertility *= helpMult
                subject.metallicity *= helpMult
            if self.effect in ["heal","resurrect"]:
                if self.effect == "resurrect":
                    helpMult *= 1.5
                if subject.permanentModifiers["herbivores"] < 1:
                    subject.herbivores *= helpMult
                if subject.permanentModifiers["carnivores"] < 1:
                    subject.carnivores *= helpMult
                if subject.permanentModifiers["fertility"] < 1:
                    subject.fertility *= helpMult
                if subject.permanentModifiers["metallicity"] < 1:
                    subject.metallicity *= helpMult
                subject.permanentModifiers["rainfall"] = clamp(subject.permanentModifiers["rainfall"]*helpMult,0,1.1)
                subject.permanentModifiers["carnivores"] = clamp(subject.permanentModifiers["carnivores"]*helpMult,0,1.1)
                subject.permanentModifiers["herbivores"] = clamp(subject.permanentModifiers["herbivores"]*helpMult,0,1.1)
                subject.permanentModifiers["vegetation"] = clamp(subject.permanentModifiers["vegetation"]*helpMult,0,1.1)
                subject.permanentModifiers["fertility"] = clamp(subject.permanentModifiers["fertility"]*helpMult,0,1.1)
                subject.permanentModifiers["metallicity"] = clamp(subject.permanentModifiers["metallicity"]*helpMult,0,1.1)
            if self.effect == "destroy":
                if roll < amount:
                    subject.biome = "ruins"
                    subject.setBiomeColor(self.myMap.biomeColors["ruins"])
                    harmMult = 0.1
                    subject.permanentModifiers["rainfall"] *= harmMult
                    subject.permanentModifiers["carnivores"] *= harmMult
                    subject.permanentModifiers["herbivores"] *= harmMult
                    subject.permanentModifiers["vegetation"] *= harmMult
                    subject.permanentModifiers["fertility"] *= harmMult
                    subject.permanentModifiers["metallicity"] *= harmMult
                    subject.herbivores *= harmMult
                    subject.carnivores *= harmMult
                    subject.fertility *= harmMult
                    subject.metallicity *= harmMult
            if self.effect == "harm":
                subject.permanentModifiers["rainfall"] *= harmMult
                subject.permanentModifiers["carnivores"] *= harmMult
                subject.permanentModifiers["herbivores"] *= harmMult
                subject.permanentModifiers["vegetation"] *= harmMult
                subject.permanentModifiers["fertility"] *= harmMult
                subject.permanentModifiers["metallicity"] *= harmMult
                subject.herbivores *= harmMult
                subject.carnivores *= harmMult
                subject.fertility *= harmMult
                subject.metallicity *= harmMult
            if self.effect == "freeze":
                subject.permanentModifiers["temperature"] *= (harmMult*0.8)
                subject.permanentModifiers["carnivores"] *= harmMult
                subject.permanentModifiers["herbivores"] *= harmMult
                subject.permanentModifiers["vegetation"] *= harmMult
                subject.permanentModifiers["fertility"] *= harmMult
                subject.herbivores *= harmMult
                subject.carnivores *= harmMult
                subject.fertility *= harmMult
            if self.effect == "burn":
                subject.permanentModifiers["temperature"] *= (helpMult*1.2)
                subject.permanentModifiers["carnivores"] *= harmMult
                subject.permanentModifiers["herbivores"] *= harmMult
                subject.permanentModifiers["rainfall"] *= harmMult
                subject.permanentModifiers["vegetation"] *= harmMult
                subject.permanentModifiers["fertility"] *= harmMult
                subject.herbivores *= harmMult
                subject.carnivores *= harmMult
                subject.fertility *= harmMult
            if self.effect == "poison":
                subject.permanentModifiers["carnivores"] *= harmMult
                subject.permanentModifiers["herbivores"] *= harmMult
                subject.permanentModifiers["vegetation"] *= harmMult
                subject.permanentModifiers["fertility"] *= harmMult
                subject.herbivores *= harmMult
                subject.carnivores *= harmMult
                subject.fertility *= harmMult
            if self.effect == "resurrect":
                if subject.biome == "ruins":
                    subject.biome = mode([n.biome for n in subject.neighbors])
                    subject.setBiomeColor(self.myMap.biomeColors[subject.biome])
            if self.effect == "curse":
                if roll < amount:
                    if obj == None:
                        obj = Curse(m=self,c=caster,a=amount)
                    obj.curseEntity(subject)
            for p in subject.entities:
                obj = self.apply(s,amount,caster,obj)
        if obj != None:
            return obj
        return None
    def justName(self):
        return self.name
    def nameFull(self):
        s = self.kind
        s += " " + self.name
        if self.creator != None:
            s += " by the " + self.creator.nameFull()
        return s
    def description(self):
        vowels = ["a","e","i","o","u"]
        s = self.name + " is a"
        if self.strength < 0.2:
            s += " weak"
        elif self.strength < 0.4:
            s += ""
        elif self.strength < 0.6:
            s += " strong"
        elif self.strength < 0.8:
            s += " powerful"
        else:
            s += " legendary"
        s += " magic "
        s += self.kind
        s += " to "
        s += self.effect
        s += " a"
        s = s + "n " + self.target if self.target[0].lower() in vowels else s + " " + self.target
        s += ".\n"
        if self.natural == False:
            s += "It was created by the " + self.creator.nameFull() + "."
        else:
            s += "It is an ability of the " + self.creator.nameFull() + "."
        return s