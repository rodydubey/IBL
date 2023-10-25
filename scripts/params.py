segmentLength = 25
detectorMeasurementInterval = 900 # seconds (15 mins), this can be 30, 45 and 60 mins for creating multiple datasets
intermittentPeriods = 60 # secons (1 min) For IBL. We randomly change IBL perimission at 60 seconds
# intermittentPeriods = 5
timeSlotForDayDivider = int(86400/detectorMeasurementInterval)
dayOfTheWeek = 1 #(Monday)
laneChangeAttemptDuration = intermittentPeriods # car will attempt to change lanes, triggers when lane is bus restricted
