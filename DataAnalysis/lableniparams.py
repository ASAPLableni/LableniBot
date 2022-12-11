class LabLeniBotParams:
	random_state = 0
	p_value_th = 0.05
	num_conv_feat = [
		"ConvTime_s",
	    "NumSamples",
	    "PersonNumUniqWords",
	    "PersonNumUniqWordsClean",
	    "PersonNumWords",
	    "PersonNumWordsClean",
	    'Mean_PersonTalk',
	    'Max_PersonTalk', 
	    'Min_PersonTalk',
	    'Diff_PersonTalk',
	    "PersonNumQuestions",
	    "AboveMaximumTime"
	]

	num_quest_feat = [
	    'Question1', 'Question2',
	    'Question3', 'Question4', 'Question5', 'Question6', 'Question7',
	    'Question8', 'Disgusto', 'Felicidad', 'Enfado', 'Miedo', 'Relajado',
	    'Sorpresa', 'Tristeza', 'Disgusto.1', 'Felicidad.1', 'Enfado.1',
	    'Miedo.1', 'Relajado.1', 'Sorpresa.1', 'Tristeza.1'
	]
