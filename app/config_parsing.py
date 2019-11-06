#MRI

EchoTime_min_t1 = 0
EchoTime_max_t1 = 25 #20

EchoTime_min_t2_stir = 10 #20
EchoTime_max_t2_stir = 120

RepetitionTime_min_t1 = 300
RepetitionTime_max_t1 = 1000

RepetitionTime_min_t2 = 1000

RepetitionTime_min_stir = 2000

InversionTime_min_stir = 40
InversionTime_max_stir = 200

InversionTime_min_flair = 300
InversionTime_max_flair = 1000

# если inversion_time > 300 до 1000 всё равно что равно нулю
# умножить значение на коэффициент магнитного поля
# If you want to add any other metadata params add it in the list, it will be 0 if there is no such line in actual dataset

METADATA_LIST = ["PatientName", "PatientID", "PatientBirthDate", "PatientSex", "PatientAge", "PatientWeight",
                 "StudyDescription", "SeriesDescription", "AcquisitionDateTime", "InstitutionName", "StationName",
                 "ManufacturerModelName",
                 "MagneticFieldStrength", "ProtocolName", "PatientPosition",
                 "EchoTime", "RepetitionTime", "RepetitionTime", "InversionTime",
                 "PulseSequenceName", "AcquisitionContrast",
                 "ImagingFrequency", "ImagedNucleus",
                 "StudyID", "SeriesNumber", "AcquisitionNumber", "InstanceNumber",
                 "PerformedProcedureStepDescription"]

# Histology

size = 1000
MAX_IMAGE_PIXELS = 25866*38912
