import ccc_models
import pandas as pd
import numpy as np

#em = ccc_models.Experience_Model("exp_test","experience",restart=True)


def train_test(model, nepochs):
    model.train(nepochs)
    result = model.test()
    try:
        return result
    except:
        return "error"


def eval_models(project, release, all_projects):

    result = {}

    model = ccc_models.Numbugs_Model(project, release, restart=restart, all_projects=all_projects)
    result['numbugs MSE'] = train_test(model, nepochs_intra)

    model = ccc_models.Buggy_Model(project, release, restart=restart, all_projects=all_projects)
    r = train_test(model, nepochs_intra)
    result['buggy precision'] = r[0]
    result['buggy recall']=r[1]

    model = ccc_models.Experience_Model(project, release, restart=restart, all_projects=all_projects)
    result['experience']=train_test(model, nepochs_intra)

    model = ccc_models.Priority_Model(project, release, restart=restart, all_projects=all_projects)
    result['priority']=train_test(model, nepochs_intra)

    model = ccc_models.Fix_Size_Model( project, release, restart=restart, all_projects=all_projects)
    result['fix size'] = train_test(model, nepochs_intra)

    return result




projects = ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa']
nepochs_intra = 0
nepochs_inter = 0
results = {"project":[], "release":[], "# samples":[], "# buggy samples":[], "numbugs MSE (intra)":[], "numbugs MSE (inter)":[], "buggy recall (intra)":[], "buggy precision (intra)":[], "buggy recall (inter)":[], "buggy precision (inter)":[], "priority (intra)":[], "priority (inter)": [], "fix size (intra)":[], "fix size (inter)":[], "experience (intra)":[], "experience (inter)":[]}
restart = False

result_types = ['numbugs MSE', 'buggy precision', 'buggy recall', 'experience', 'priority', 'fix size']


for project in projects:

    for release in [0,1,2]:

        df = pd.read_csv("../files/nabats_dataset.csv")
        print(df.shape)
        #df = df.loc[(df['project']==project)&(df['release_id']==release)]

        test_samples = df.loc[(df['project']==project)&(df['release_id']==release+1)]
        train_samples = df.loc[(df['project']==project)&(df['release_id']==release)]

        print(test_samples.shape)
        print(train_samples.shape)

        results["# samples"].append(train_samples.shape[0])
        results["# buggy samples"].append(train_samples.loc[df['num_bugs']>0].shape[0])
        results['project'].append(project)
        results['release'].append(release)
        print(df.shape)


        # Intra
        if (train_samples.shape[0] > 0) and test_samples.shape[0]>0:
            result = eval_models(project, release, False) #False for not all projects
            for r in result_types:
                results[r+" (intra)"].append(result[r])
        else:
            for r in result_types:
                results[r+" (intra)"].append(np.nan)

        print(df.shape)

        # Inter
        if train_samples.shape[0] > 0:
            result = eval_models(project, release, True) #True for "all projects"
            for r in result_types:
                results[r+" (inter)"].append(result[r])
        else:
            for r in result_types:
                results[r+" (inter)"].append(np.nan)


        print(df.shape)

    #model = ccc_models.Numbugs_Model(project, restart=restart, all_projects=True)
    #results['numbugs MSE (inter)'].append(train_test(model, nepochs_inter))

    #model = ccc_models.Buggy_Model(project, restart=restart, all_projects=True)
    #r = train_test(model, nepochs_inter)
    #results['buggy (inter) precision'].append(r[0])
    #results['buggy (inter) recall'].append(r[1])

    #model = ccc_models.Experience_Model(project, restart=restart, all_projects=True)
    #results['experience (inter)'].append(train_test(model, nepochs_inter))

    #model = ccc_models.Priority_Model(project, restart=restart, all_projects=True)
    #results['priority (inter)'].append(train_test(model, nepochs_inter))

    #model = ccc_models.Fix_Size_Model(project, restart=restart, all_projects=True)
    #results['fix size (inter)'].append(train_test(model, nepochs_inter))

    #IMPORTANT NOTE!! Recall is replaced with AUC and precision is set to zero in ccc_models.py!
    result_df = pd.DataFrame(results)
    result_df.to_csv("../ccc_model_results_MSE_TEST.csv")
