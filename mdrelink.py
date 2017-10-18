import sublime, sublime_plugin, math

def cleanup(self, edit):
    redundantNewLine = self.view.find_all("\[.+?\]\: [http|\/|\.\/|\~\/].+?\n{2,}\[.+?\]\: [http|\/|\.\/|\~\/].+?\n")

    trimNewLine = []
    self.view.find_all("(\[.+?\]\: [http|\/|\.\/|\~\/].+?\n)\n+(\[.+?\]\: [http|\/|\.\/|\~\/].+?\n)", sublime.IGNORECASE, "\\1\\2", trimNewLine)
    
    for i, r in enumerate(redundantNewLine):
        self.view.replace(edit, r, trimNewLine[i])


def reorderReferences(self, edit):
    references = []
    self.view.find_all("(\[\d+\])[^:]", sublime.IGNORECASE, "\\1", references)
    for i, ref in enumerate(references):
        regions = self.view.find_all(ref, sublime.LITERAL)
        regions.reverse()
        pad = int(math.ceil(math.log(len(references), 10)))
        for r in regions:
            self.view.replace(edit, r, "[#{:0{padding}d}#]".format(i+1, padding = pad))

    # remove #
    hashedReferences = []
    hashedRegion = self.view.find_all("\[\#(\d+)\#\]", sublime.IGNORECASE, "[\\1]", hashedReferences)
    hashedReferences.reverse()
    hashedRegion.reverse()
    for i, r in enumerate(hashedRegion):
        self.view.replace(edit, r, hashedReferences[i])

    # sort
    texts = []
    newRegions = self.view.find_all("^(\[\d+\]:.+?\n)", sublime.IGNORECASE, "\\1", texts)
    newRegions.reverse()
    for i, r in enumerate(newRegions):
        self.view.erase(edit, r)
    
    for address in sorted(texts):
        self.view.insert(edit, self.view.size(), address)


class mdrelinkCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        oldlinks = []
        self.view.find_all("^\s*(\[\d+\]):", sublime.IGNORECASE, "\\1", oldlinks)

        # get all link location
        links = self.view.find_all("\[.+?\](\([http|\/|\.\/|\~\/].+?\))")

        # get link's text
        texts = []
        self.view.find_all("(\[.+?\])\([http|\/|\.\/|\~\/].+?\)", sublime.IGNORECASE, "\\1", texts)

        # get link's addresses
        addresses = []
        self.view.find_all("\[.+?\]\(([http|\/|\.\/|\~\/].+?)\)", sublime.IGNORECASE, "\\1", addresses)

        addresses.reverse()

        if len(links) > 0:
            self.view.insert(edit, self.view.size(), '\n\n')

        counter = 1
        newnumbers = []

        for i, r in enumerate(links):
            while '['+str(counter)+']' in oldlinks:
                counter += 1
            oldlinks.append('['+str(counter)+']')
            # line = texts[i] +': '+ addresses.pop() + '\n'
            line = '[' + str(counter) +']: '+ addresses.pop() + '\n'
            newnumbers.append('['+str(counter)+']')
            self.view.insert(edit, self.view.size(), line)

        for r in reversed(links):
            self.view.replace(edit, r, texts.pop() + newnumbers.pop())
            # self.view.replace(edit, r, texts.pop())

        # Cleanup
        cleanup(self, edit)
        reorderReferences(self, edit)