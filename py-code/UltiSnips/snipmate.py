# encoding: utf-8

import sys
import re
import os

def convert_snippet_contents(content):
    " If the snippet contains snipmate style substitutions, convert them to ultisnips style "
    content = re.sub("`([^`]+`)", "`!v \g<1>", content)
    return content

# convert a snipmate .snippet lines to UltiSnips
def convert_snippet_lines(name, lines):
    " One file per filetype "
    retval = ""
    state = 0
    for line in lines:
        # Ignore empty lines
        if line.strip() == "":
            continue
        # The rest of the handling is stateful
        if state == 0:
            # Find snippet start. Keep comments.
            if line[:8] == "snippet ":
                snippet_info = re.match("(\S+)\s*(.*)", line[8:])
                if not snippet_info:
                    print >> sys.stderr, "Warning: Malformed snippet\n %s:%s\n" % (name, line)
                    continue
                retval += 'snippet %s "%s"' % (snippet_info.group(1), snippet_info.group(2) if snippet_info.group(2) else snippet_info.group(1)) + "\n"
                state = 1
                snippet = ""
            elif line[:1] == "#":
                retval += line
                state = 0
        elif state == 1:
            # First line of snippet: Get indentation
            whitespace = re.search("^\s+", line)
            if not whitespace:
                print >> sys.stderr, "Warning: Malformed snippet, content not indented.\n"
                retval += "endsnippet\n\n"
                state = 0
            else:
                whitespace = whitespace.group(0)
                snippet += line[len(whitespace):]
                state = 2
        elif state == 2:
            # In snippet: If indentation level is the same, add to snippet. Else end snippet.
            if line[:len(whitespace)] == whitespace:
                snippet += line[len(whitespace):]
            else:
                retval += convert_snippet_contents(snippet) + "endsnippet\n\n"
                #Copy-paste the section from state=0 so that we don't skip every other snippet
                if line[:8] == "snippet ":
                    snippet_info = re.match("(\S+)\s*(.*)", line[8:])
                    if not snippet_info:
                        print >> sys.stderr, "Warning: Malformed snippet\n %s\n" % line
                        continue
                    retval += 'snippet %s "%s"' % (snippet_info.group(1), snippet_info.group(2) if snippet_info.group(2) else snippet_info.group(1)) + "\n"
                    state = 1
                    snippet = ""
                elif line[:1] == "#":
                    retval += line
                    state = 0
    if state == 2:
        retval += convert_snippet_contents(snippet) + "endsnippet\n\n"
    return retval