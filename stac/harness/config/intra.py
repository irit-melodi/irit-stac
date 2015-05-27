"""Configuration helpers for using the intra-inter sentential stuff"""

from attelo.harness.config import (EvaluationConfig,
                                   Keyed)
from .common import (Settings, combined_key)


def combine_intra(econfs, kconf, primary='intra'):
    """Combine a pair of EvaluationConfig into a single IntraInterParser

    Parameters
    ----------
    econfs: IntraInterPair(EvaluationConfig)

    kconf: Keyed(parser constructor)

    primary: ['intra', 'inter']
        Treat the intra/inter config as the primary one for the key
    """
    if primary == 'intra':
        econf = econfs.intra
    elif primary == 'inter':
        econf = econfs.inter
    else:
        raise ValueError("'primary' should be one of intra/inter: " + primary)

    parsers = econfs.fmap(lambda e: e.parser.payload)
    subsettings = econfs.fmap(lambda e: e.settings)
    learners = econfs.fmap(lambda e: e.learner)
    settings = Settings(key=combined_key(kconf, econf.settings),
                        intra=True,
                        oracle=econf.settings.oracle,
                        children=subsettings)
    kparser = Keyed(combined_key(kconf, econf.parser),
                    kconf.payload(parsers))
    if learners.intra.key == learners.inter.key:
        learner_key = learners.intra.key
    else:
        learner_key = '{}S_D{}'.format(learners.intra.key,
                                       learners.inter.key)
    return EvaluationConfig(key=combined_key(learner_key, kparser),
                            settings=settings,
                            learner=learners,
                            parser=kparser)
