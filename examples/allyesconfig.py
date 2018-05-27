# Works like 'make allyesconfig'. Verified by the test suite to generate output
# identical to 'make allyesconfig', for all ARCHES.
#
# This example is implemented a bit differently from allnoconfig.py to
# demonstrate some other possibilities. A variant similar to
# allnoconfig_simpler.py could be constructed too.
#
# In theory, we need to handle choices in two different modes:
#
#   y: One symbol is y, the rest are n
#   m: Any number of symbols are m, the rest are n
#
# Only tristate choices can be in m mode.
#
# In practice, no m mode choices appear for allyesconfig as of 4.14, as
# expected, but we still handle them here for completeness. Here's a convoluted
# example of how you might get an m-mode choice even during allyesconfig:
#
#   choice
#           tristate "weird choice"
#           depends on m
#
#   ...
#
#   endchoice
#
#
# Usage:
#
#   $ make [ARCH=<arch>] scriptconfig SCRIPT=Kconfiglib/examples/allyesconfig.py

from kconfiglib import Kconfig, Choice
import sys

kconf = Kconfig(sys.argv[1])

while True:
    changed = False

    for sym in kconf.defined_syms:
        # Choices are handled separately below
        if sym.choice:
            continue

        # Set the symbol to the highest assignable value, unless it already has
        # that value. sym.assignable[-1] gives the last element in assignable.
        if sym.assignable and sym.tri_value < sym.assignable[-1]:
            sym.set_value(sym.assignable[-1])
            changed = True

    for choice in kconf.choices:
        # Same logic as above for choices
        if choice.assignable and choice.tri_value < choice.assignable[-1]:
            choice.set_value(choice.assignable[-1])

            # For y-mode choices, we just let the choice get its default
            # selection. For m-mode choices, we set all choice symbols to m.
            if choice.tri_value == 1:
                for sym in choice.syms:
                    sym.set_value(1)

            changed = True

    # Do multiple passes until we longer manage to raise any symbols or
    # choices, like in allnoconfig.py
    if not changed:
        break

kconf.write_config(".config")
