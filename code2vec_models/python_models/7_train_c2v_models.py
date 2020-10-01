import c2v_models
import pandas as pd
import numpy as np

#em = c2v_models.Experience_Model("exp_test","experience",restart=True)


def train_test(model, nepochs):
    model.train(nepochs)
    result = model.test()
    try:
        return result
    except:
        return "error"


def eval_models(project, release, all_projects, nepochs):

    result = {}

    #model = c2v_models.Numbugs_Model(project, release, restart=restart, all_projects=all_projects)
    #result['numbugs MSE'] = train_test(model, nepochs_intra)

    model = c2v_models.Buggy_Model(project, release, restart=restart, all_projects=all_projects)
    r = train_test(model, nepochs)
    result['buggy precision'] = r[0]
    result['buggy recall']=r[1]

    model = c2v_models.Experience_Model(project, release, restart=restart, all_projects=all_projects)
    result['experience']=train_test(model, nepochs)

    model = c2v_models.Priority_Model(project, release, restart=restart, all_projects=all_projects)
    result['priority']=train_test(model, nepochs)

    model = c2v_models.Fix_Size_Model( project, release, restart=restart, all_projects=all_projects)
    result['fix size'] = train_test(model, nepochs)

    return result




projects = ['accumulo', 'bookkeeper', 'camel', 'cassandra', 'cxf', 'derby', 'hive', 'openjpa']
nepochs_intra = 0
nepochs_inter = 0
results = {"project":[], "release":[], "# samples":[], "# buggy samples":[], "buggy recall (intra)":[], "buggy precision (intra)":[], "buggy recall (inter)":[], "buggy precision (inter)":[], "priority (intra)":[], "priority (inter)": [], "fix size (intra)":[], "fix size (inter)":[], "experience (intra)":[], "experience (inter)":[]}
restart = False

result_types = ['buggy precision', 'buggy recall', 'experience', 'priority', 'fix size']


for project in projects:

    for release in [0,1,2]:

        df = pd.read_csv("../files/"+project+"/train_data5.csv")
        #df = df.loc[(df['project']==project)&(df['release_id']==release)]

        test_samples = df.loc[(df['project']==project)&(df['release_id']==release+1)]
        train_samples = df.loc[(df['project']==project)&(df['release_id']==release)]



        results["# samples"].append(train_samples.shape[0])
        results["# buggy samples"].append(train_samples.loc[df['buggy']==1].shape[0])
        results['project'].append(project)
        results['release'].append(release)
        print(project,release,df.shape)
        print("test samples:",test_samples.shape)
        print("train samples:",train_samples.shape)
        print('-')


        # Intra
        if (train_samples.shape[0] > 0) and test_samples.shape[0]>0:
            result = eval_models(project, release, False, nepochs_intra) #False for not all projects
            for r in result_types:
                results[r+" (intra)"].append(result[r])
        else:
            for r in result_types:
                results[r+" (intra)"].append(np.nan)


        # Inter
        if train_samples.shape[0] > 0:
            result = eval_models(project, release, True, nepochs_inter) #True for "all projects"
            for r in result_types:
                results[r+" (inter)"].append(result[r])
        else:
            for r in result_types:
                results[r+" (inter)"].append(np.nan)




    result_df = pd.DataFrame(results)
    result_df.to_csv("../c2v_model_results.csv")




#
