"""An enforced observation deadline, not a guarantee of startup performance.

The manager keeps TimeoutStartSec=40. This adapter allocates <40 seconds from the
single bot start request through READY, identity and admission receipt checks.
At the deadline outcome is STOP/manual inspection; the manager may still run for
its remaining budget. No automatic kill/retry/restore or app benchmark is implied.
The old input name startup_bound_seconds denotes this allocated observation
budget when supplied by the host binder, never a measured worst-case latency.
"""
from scripts import phase16_bot_maintenance as core
from scripts import phase16_bot_service_operations as services

require=core.require

def assess_budget(*,admission_seconds,manager_start_seconds,observation_seconds=39):
    require(all(type(x) is int for x in (admission_seconds,manager_start_seconds,observation_seconds)) and
            manager_start_seconds==40 and 1<=admission_seconds<observation_seconds<manager_start_seconds,
            'startup_budget')
    return dict(scope='ENFORCED_OBSERVATION_BUDGET',admission_seconds=admission_seconds,
        manager_start_seconds=manager_start_seconds,startup_observation_budget_seconds=observation_seconds,
        unallocated_seconds=observation_seconds-admission_seconds,startup_success_guaranteed=False,
        deadline_outcome='UNKNOWN_MANUAL_INSPECTION_NO_RETRY')

class BudgetedServiceOperations(services.ServiceOperations):
    def __init__(self,*args,startup_observation_budget_seconds=39,**kwargs):
        super().__init__(*args,**kwargs)
        self.startup_assessment=assess_budget(admission_seconds=self.journal.manifest['admission_seconds'],
            manager_start_seconds=self.journal.manifest['unit_baseline'][core.BOT]['start_seconds'],
            observation_seconds=startup_observation_budget_seconds)
        self.startup_observation=None

    def candidate_start(self):
        original=self.client.run
        started=deadline=None
        def remaining():
            value=deadline-self.clock()
            require(value>0,'service_action_deadline')
            return value
        def run(argv,seconds):
            nonlocal started,deadline
            if argv==['systemctl','--no-block','start',core.BOT]:
                require(deadline is None,'service_action_deadline')
                require(self.client.bus_property(core.BOT,'Service','TimeoutStartUSec','t')==40000000,'startup_budget')
                started=self.clock();deadline=started+self.startup_assessment['startup_observation_budget_seconds']
            if deadline is not None:seconds=min(seconds,remaining())
            value=original(argv,seconds)
            if deadline is not None:remaining()
            return value
        self.client.run=run
        try:
            super().candidate_start()
            require(deadline is not None,'startup_budget')
            remaining()
            self.startup_observation=dict(self.startup_assessment,elapsed_seconds=self.clock()-started)
        finally:self.client.run=original
