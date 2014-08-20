from tornado.web import authenticated
from tornado.web import HTTPError

from amgut.handlers.base_handlers import BaseHandler
from amgut.util import AG_DATA_ACCESS

class ParticipantOverviewHandler(BaseHandler):
    @authenticated
    def post(self, participant_name):
        skid = self.current_user
        ag_login_id = AG_DATA_ACCESS.get_user_for_kit(skid)
        participant_type = self.get_argument('participant_type')

        try:
            survey_details = AG_DATA_ACCESS.getAGSurveyDetails(ag_login_id,
                participant_name)
        except:
            raise HTTPError(404, "Could not retrieve survey details for "
                            "participant '%s'" % participant_name)

        # The defaults must be added to the page as hidden form inputs, in
        # case the user clicks edit survey
        defaults = {}
        for k, v in sorted(survey_details.items()):
            suffix = '_default'
            # do NOT suffix these fields
            if k in ('consent', 'parent_1_name', 'parent_2_name',
                     'deceased_parent', 'participant_email',
                     'participant_name', 'ag_login_id'):
                defaults[k] = v

            # if the name of the field ends in a number, it's a multiple, and should
            # be written out differently UNLESS it's migraine_factor_# or
            # mainfactor_other_#
            # don't like to special-case like this, but there's no other way to tell
            # what's a multiple and what's not
            if k[-1] in map(str, range(10)) \
                    and not k.startswith('migraine_factor_') \
                    and not k.startswith('mainfactor_other_'):
                k = k.rsplit('_', 1)[0]
                defaults[k+'_default[]'] = v

        # Get the list of samples for this participant
        samples = AG_DATA_ACCESS.getParticipantSamples(ag_login_id,
                                                       participant_name)

        self.render('participant_overview.html', defaults=defaults, skid=skid,
                    participant_name=participant_name,
                    participant_type=participant_type, samples=samples)
