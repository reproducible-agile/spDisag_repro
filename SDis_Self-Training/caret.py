import warnings

from config.definitions import ROOT_DIR
warnings.filterwarnings("ignore", category=DeprecationWarning)

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from catboost import CatBoostRegressor, MultiRegressionCustomObjective
from sklearn.model_selection import RandomizedSearchCV
import numpy as np, math
import nputils as npu
from numpy import random
#import xgboost as xgb
import time
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
#matplotlib.use('TKAgg')
import seaborn as sns
from mainFunctions.basic import createFolder
"""
import kerasutils as ku
import xgboost as xgb
import skimage.measure
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.callbacks import ReduceLROnPlateau
from tensorflow.keras import utils
import tensorflow as tf
"""
SEED = 42

def fitlm(X, y):
    mod = LinearRegression()
    mod = mod.fit(X, y)
    return mod
"""
def fitsgdregressor(X, y, batchsize, lrate, epoch):
    mod = SGDRegressor(max_iter=epoch, alpha=0, learning_rate='constant', eta0=lrate, verbose=1)
    mod = mod.fit(X, y)
    return mod
"""

def plot_feature_importance(importance,names,model_type, casestudy,city):
    
    #Create arrays from feature importance and feature names
    feature_importance = np.array(importance)
    feature_names = np.array(names)
    
    #Create a DataFrame using a Dictionary
    data={'feature_names':feature_names,'feature_importance':feature_importance}
    fi_df = pd.DataFrame(data)
    
    #Sort the DataFrame in order decreasing feature importance
    fi_df.sort_values(by=['feature_importance'], ascending=False,inplace=True)
    
    #Define size of bar plot
    plt.figure(figsize=(10,8))
    #Plot Searborn bar chart
    sns.barplot(x=fi_df['feature_importance'], y=fi_df['feature_names'])
    #Add chart labels
    plt.title(model_type + '_FEATURE IMPORTANCE')
    plt.xlabel('FEATURE IMPORTANCE')
    plt.ylabel('FEATURE NAMES')
    createFolder(ROOT_DIR + "/Results/{2}/{0}_importance".format(model_type,casestudy,city))
    plt.savefig(ROOT_DIR + "/Results/{2}/{0}_importance/{1}.png".format(model_type,casestudy,city), dpi=300, bbox_inches='tight')
    
def fitrf(X, y, ROOT_DIR, casestudy,city):
    # mod = RandomForestRegressor(n_estimators = 10, random_state=SEED) # n_estimators = 10
    mod = RandomForestRegressor(n_estimators = 100, random_state=SEED, criterion='squared_error') # absolute_error, 'squared_error'
    mod = mod.fit(X, y)
    feature_names = [f"feature {i}" for i in range(X.shape[1])]
    importances = mod.feature_importances_
    plot_feature_importance(importances, feature_names, 'aprf', casestudy,city)  
    
    return mod

def fitmulti(X, y):

    wrapper = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=SEED, criterion='squared_error'))# mod = RandomForestRegressor(n_estimators = 10, random_state=SEED) # n_estimators = 10
    mod = wrapper.fit(X, y)
    
    return mod

class MultiRMSEObjectiveI(MultiRegressionCustomObjective):
                
        def calc_ders_multi(self, approxes, targets, weight):           
                assert len(approxes) == len(targets)
                sum = np.sum(approxes[0:-1])
                error1 = 2 * (sum - approxes[-1])
                error2 = 2 * (approxes[-1] - sum)
                grad = []
                hess = [[0 for j in range(len(targets))] for i in range(len(targets))]
                for index in range(len(targets)):
                        if index==len(targets) -1 : der1 = ( 2*(targets[index] - approxes[index]) - error2 ) * weight
                        else: der1 = ( 2*(targets[index] - approxes[index]) + error1 ) * weight
                        der2 = -weight
                        grad.append(der1)
                        hess[index][index] = der2
                return (grad, hess)

class MultiRMSEObjectiveS(MultiRegressionCustomObjective):
                
        def calc_ders_multi(self, approxes, targets, weight):           
                assert len(approxes) == len(targets)
                sum1 = np.sum(approxes)
                sum2 = np.sum(targets)
                grad = []
                hess = [[0 for j in range(len(targets))] for i in range(len(targets))]
                for index in range(len(targets)):
                        der1 = ((targets[index] - approxes[index]) + (sum2-sum1)) * weight
                        der2 = -weight
                        grad.append(der1)
                        hess[index][index] = der2
                return (grad, hess)

class MultiRMSEObjectiveA(MultiRegressionCustomObjective):
                
        def calc_ders_multi(self, approxes, targets, weight):  
                # Assume that there are 5 output quantities. 
                # The first three should be summed to get the total, and the last two form another group that should be summed to get the total.                           
                assert len(approxes) == len(targets)
                sum1g1 = np.sum(approxes[0:5])
                sum2g1 = np.sum(targets[0:5])
                sum1g2 = np.sum(approxes[5:-1])
                sum2g2 = np.sum(targets[5:-1])
                grad_g1 = np.sign(sum2g1-sum1g1)
                grad_g2 = np.sign(sum2g2-sum1g2)
                grad = []
                hess = [[0 for j in range(len(targets))] for i in range(len(targets))]
                for index in range(len(targets)):
                        der1 = ((targets[index] - approxes[index]) + grad_g1 + grad_g2) * weight
                        der2 = -weight
                        grad.append(der1)
                        hess[index][index] = der2
                return (grad, hess)

class MultiRMSEObjectiveB(MultiRegressionCustomObjective):
                
        def calc_ders_multi(self, approxes, targets, weight):  
                # Assume that there are 5 output quantities. 
                # The first three should be summed to get the total, and the last two form another group that should be summed to get the total.                           
                assert len(approxes) == len(targets)
                sum1g1 = np.sum(approxes[0:5])
                sum2g1 = np.sum(targets[0:5])
                sum1g2 = np.sum(approxes[5:-3])
                sum2g2 = np.sum(targets[5:-3])
                sum1g3 = np.sum(approxes[-3:-1])
                sum2g3 = np.sum(targets[-3:-1])
                grad_g1 = np.sign(sum2g1-sum1g1)
                grad_g2 = np.sign(sum2g2-sum1g2)
                grad_g3 = np.sign(sum2g3-sum1g3)
                grad = []
                hess = [[0 for j in range(len(targets))] for i in range(len(targets))]
                for index in range(len(targets)):
                        der1 = ((targets[index] - approxes[index]) + grad_g1 + grad_g2 + grad_g3) * weight
                        der2 = -weight
                        grad.append(der1)
                        hess[index][index] = der2
                return (grad, hess)
                                
def fitcatbr(X, y, casestudy,city):
    mod = CatBoostRegressor(iterations=500, learning_rate=0.01, depth=5, task_type='CPU', thread_count=-1, loss_function=MultiRMSEObjectiveB(), eval_metric='MultiRMSE') #iterations=200, learning_rate=0.1, depth=5
    mod = mod.fit(X, y)
    feature_names = [f"feature {i}" for i in range(X.shape[1])]
    plot_feature_importance(mod.get_feature_importance(), feature_names, 'CATBOOST', casestudy, city)   
    
    return mod

def fitxgbtree(X, y):
    # gbm = xgb.XGBRegressor(seed=SEED)
    gbm = xgb.XGBRegressor(seed=SEED, eval_metric='mae')
    # g13 = {'colsample_bytree': [0.4, 0.5], 'n_estimators': [50, 75, 100], 'max_depth': [3, 5, 7]}
    # # g14 = {'colsample_bytree': [0.3, 0.4, 0.5], 'n_estimators': [50, 75, 100], 'max_depth': [3, 5, 7]}
    # mod = RandomizedSearchCV(param_distributions=g13, estimator=gbm,
    #                         scoring='neg_mean_squared_error', n_iter=5, cv=4,
    #                         verbose=1)
    # mod = mod.fit(X, y)

    mod = gbm.fit(X, y)
    return mod

def fitxgbtreeM(X, y):
    # gbm = xgb.XGBRegressor(seed=SEED)
    gbm = xgb.XGBRegressor(seed=SEED, eval_metric='mae')
    # g13 = {'colsample_bytree': [0.4, 0.5], 'n_estimators': [50, 75, 100], 'max_depth': [3, 5, 7]}
    # # g14 = {'colsample_bytree': [0.3, 0.4, 0.5], 'n_estimators': [50, 75, 100], 'max_depth': [3, 5, 7]}
    # mod = RandomizedSearchCV(param_distributions=g13, estimator=gbm,
    #                         scoring='neg_mean_squared_error', n_iter=5, cv=4,
    #                         verbose=1)
    # mod = mod.fit(X, y)

    mod = gbm.fit(X, y)
    return mod

def fit(X, y, p, method, batchsize, lrate, epoch, casestudy,city):
    X = X.reshape((-1, X.shape[2]))
    y = np.ravel(y)

    relevantids = np.where(~np.isnan(y))[0]
    relevsamples = np.random.choice(len(relevantids), round(len(relevantids) * p[0]), replace=False)
    idsamples = relevantids[relevsamples]
    print('| --- Number of instances (All, >0, X%>0):', y.shape[0], len(relevantids), len(idsamples))

    # Stratified sampling
    # numstrats = 10
    # bins = np.linspace(0, np.max(y)+0.0000001, numstrats+1)
    # digitized = np.digitize(y, bins)
    # numsamp = round(len(relevantids) * p[0] / numstrats + 0.5)
    # samplevals = [np.random.choice(np.where(digitized == i)[0], min(numsamp, len(y[digitized == i])), replace=False) for
    #               i in range(1, len(bins))]
    # idsamples = [item for sublist in samplevals for item in sublist]
    # np.random.shuffle(idsamples)

    X = X[idsamples,:]
    y = y[idsamples]
    # y = np.log(1+y)

    if(method.endswith('lm')):
        print('|| Fit: Linear Model')
        return fitlm(X, y)
    if (method.endswith('sgdregressor')):
        print('|| Fit: SGD Regressor')
        #return fitsgdregressor(X, y, batchsize, lrate, epoch)
    elif(method.endswith('rf')):
        print('|| Fit: Random Forests')
        return fitrf(X, y, ROOT_DIR, casestudy,city)
    elif(method.endswith('xgbtree')):
        print('|| Fit: XGBTree')
        #return fitxgbtree(X, y)
    else:
        return None

def fitM(X, y, p, method, batchsize, lrate, epoch, ROOT_DIR, casestudy,city):
    
    X = X.reshape((-1, X.shape[2]))
    y = y.reshape((-1, y.shape[2]))
    
    relevantids = np.where(~np.isnan(y))[0]
    relevsamples = np.random.choice(len(relevantids), round(len(relevantids) * p[0]), replace=False)
    idsamples = relevantids[relevsamples]
    print('| --- Number of instances (All, >0, X%>0):', y.shape[0], len(relevantids), len(idsamples))

    X = X[idsamples,:]
    #y = y[idsamples]
    y = y[idsamples,:]
    # y = np.log(1+y)

    if(method.endswith('lm')):
        print('|| Fit: Linear Model')
        return fitlm(X, y)
    if (method.endswith('sgdregressor')):
        print('|| Fit: SGD Regressor')
        #return fitsgdregressor(X, y, batchsize, lrate, epoch)
    elif(method.endswith('rf')):
        print('|| Fit: Random Forests')
        return fitrf(X, y, ROOT_DIR, casestudy,city)
    elif(method.endswith('mltr')):
        print('|| Fit: Multi Output Regressor')
        return fitmulti(X, y)
    elif(method.endswith('catbr')):
        print('|| Fit: CatBoostRegressor')
        return fitcatbr(X, y, casestudy,city)
    elif(method.endswith('xgbtree')):
        print('|| Fit: XGBTree')
        return fitxgbtreeM(X, y)
    else:
        return None

"""
def get_callbacks():
    return [
        # ReduceLROnPlateau(monitor='loss', min_delta=0.0, patience=3, factor=0.1, min_lr=5e-6, verbose=1),
        # EarlyStopping(monitor='loss', min_delta=0.001, patience=3, verbose=1, restore_best_weights=True)
        EarlyStopping(monitor='loss', min_delta=0.01, patience=3, verbose=1, restore_best_weights=True)
    ]
"""
"""
class DataGenerator(utils.Sequence):
    'Generates data for Keras'

    def __init__(self, Xdataset, ydataset, idsamples, batch_size, p):
        'Initialization'
        self.X, self.y = Xdataset, ydataset
        self.batch_size = batch_size
        self.p = p
        self.idsamples = idsamples

    def __len__(self):
        'Denotes the number of batches per epoch'
        return math.ceil(len(self.idsamples) / self.batch_size)

    def __getitem__(self, idx):
        'Generate one batch of data'
        idsamplesbatch = self.idsamples[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_X = self.X[idsamplesbatch]
        batch_X[np.isnan(batch_X)] = 0 ## Alterado
        batch_y = self.y[idsamplesbatch]
        return np.array(batch_X), np.array(batch_y)

def fitcnn(X, y, p, cnnmod, cnnobj, casestudy, epochs, batchsize, extdataset):
    tf.random.set_seed(SEED)

    # Reset model weights
    print('------- LOAD INITIAL WEIGHTS')
    cnnobj.load_weights('Temp/models_' + casestudy + '.h5')

    if cnnmod == 'lenet':
        print('| --- Fit - 1 resolution Le-Net')

        # Select midd pixel from patches
        middrow, middcol = int((y.shape[1]-1)/2), int(round((y.shape[2]-1)/2))
        y = y[:,middrow,middcol,0]

        relevantids = np.where(~np.isnan(y))[0]
        relevsamples = np.random.choice(len(relevantids), round(len(relevantids) * p[0]), replace=False)
        idsamples = relevantids[relevsamples]
        print('Number of instances (All, >0, X%>0):', y.shape[0], len(relevantids), len(idsamples))

        if extdataset:
            newX, newy = npu.extenddataset(X[idsamples, :, :, :], y[idsamples], transf=extdataset)
            return cnnobj.fit(newX, newy, epochs=epochs, batch_size=batchsize)
        else:
            Xfit = X[idsamples, :, :, :]
            yfit = y[idsamples]
            hislist = [cnnobj.fit(Xfit, yfit, epochs=epochs, batch_size=batchsize)]
            return hislist

    elif cnnmod == 'vgg':
        print('| --- Fit - 1 resolution VGG-Net')

        # Select midd pixel from patches
        middrow, middcol = int((y.shape[1]-1)/2), int(round((y.shape[2]-1)/2))
        y = y[:,middrow,middcol,0]

        relevantids = np.where(~np.isnan(y))[0]
        relevsamples = np.random.choice(len(relevantids), round(len(relevantids) * p), replace=False)
        idsamples = relevantids[relevsamples]
        print('Number of instances (All, >0, X%>0):', y.shape[0], len(relevantids), len(idsamples))

        if extdataset:
            newX, newy = npu.extenddataset(X[idsamples, :, :, :], y[idsamples], transf=extdataset)
            return cnnobj.fit(newX, newy, epochs=epochs, batch_size=batchsize)
        else:
            return cnnobj.fit(X[idsamples, :, :, :], y[idsamples], epochs=epochs, batch_size=batchsize)

    elif cnnmod == 'uenc':
        print('| --- Fit - 1 resolution U-Net encoder')

        # Select midd pixel from patches
        middrow, middcol = int((y.shape[1]-1)/2), int(round((y.shape[2]-1)/2))
        y = y[:,middrow,middcol,0]

        relevantids = np.where(~np.isnan(y))[0]
        relevsamples = np.random.choice(len(relevantids), round(len(relevantids) * p), replace=False)
        idsamples = relevantids[relevsamples]
        print('Number of instances (All, >0, X%>0):', y.shape[0], len(relevantids), len(idsamples))

        if extdataset:
            newX, newy = npu.extenddataset(X[idsamples, :, :, :], y[idsamples], transf=extdataset)
            return cnnobj.fit(newX, newy, epochs=epochs, batch_size=batchsize)
        else:
            return cnnobj.fit(X[idsamples, :, :, :], y[idsamples], epochs=epochs, batch_size=batchsize)

    elif cnnmod.endswith('unet'):
        # Compute midd pixel from patches
        middrow, middcol = int((y.shape[1]-1)/2), int(round((y.shape[2]-1)/2))

        # Train only with patches having middpixel different from NaN
        relevantids = np.where(~np.isnan(y[:,middrow,middcol,0]))[0]

        # Train only with patches having finit values in all pixels
        # relevantids = np.where(~np.isnan(y).any(axis=(1,2,3)))[0]

        if len(p) > 1:
            relevsamples = np.random.choice(len(relevantids), round(len(relevantids)), replace=False)
        else:
            relevsamples = np.random.choice(len(relevantids), round(len(relevantids) * p[0]), replace=False)
        idsamples = relevantids[relevsamples]

        # Stratified sampling
        # numstrats = 10
        # sumaxis0 = np.sum(y, axis=(1, 2, 3))
        # bins = np.linspace(0, np.nanmax(sumaxis0)+0.0000001, numstrats+1)
        # digitized = np.digitize(sumaxis0, bins)
        # numsamp = round(len(relevantids) * p[0] / numstrats + 0.5)
        # samplevals = [np.random.choice(np.where(digitized == i)[0], min(numsamp, len(sumaxis0[digitized == i])), replace=False) for
        #               i in range(1, len(bins))]
        # idsamples = [item for sublist in samplevals for item in sublist]
        # np.random.shuffle(idsamples)

        print('Number of instances (All, >0, X%>0):', y.shape[0], len(relevantids), len(idsamples))

        if(cnnmod == 'unet'):
            if extdataset:
                Xfit = X[idsamples, :, :, :]
                yfit = y[idsamples]
                yfit[np.isnan(yfit)] = 0
                newX, newy = npu.extenddataset(Xfit, yfit, transf=extdataset)
                hislist = [cnnobj.fit(newX, newy, epochs=epochs, batch_size=batchsize)]
                return hislist
            else:
                if len(p) > 1:
                    print('| --- Fit-generator - 1 resolution U-Net Model')
                    hislist = []
                    Xgen = X[idsamples, :, :, :]
                    ygen = y[idsamples]
                    for i in range(len(p)):
                        cnnobj.load_weights('models_' + casestudy + '.h5')
                        mod = cnnobj.fit(generator(Xgen, ygen, batchsize),
                                         steps_per_epoch=round(len(idsamples) * p[i] / batchsize), epochs=epochs)
                        hislist.append(mod)
                        cnnobj.save_weights('snapshot_' + casestudy + '_' + str(i) + '.h5')
                    return hislist
                else:
                    print('| --- Fit - 1 resolution U-Net Model')
                    # Xfit = X[idsamples, :, :, :] ## Comentado
                    # yfit = y[idsamples] ## Comentado
                    # ctignore = np.isnan(Xfit) ## Comentado
                    # Xfit[ctignore] = 0 ## Comentado

                    # yfit = np.log(1+yfit)
                    # yfit[np.isnan(yfit)] = 0
                    # hislist = [cnnobj.fit(Xfit, yfit, epochs=epochs, batch_size=batchsize)]

                    training_generator = DataGenerator(X, y, idsamples, batch_size=batchsize, p=p[0])
                    hislist = [cnnobj.fit(training_generator, epochs=epochs)]

                    # hislist = [cnnobj.fit(Xfit, yfit, epochs=epochs, batch_size=batchsize, callbacks=get_callbacks())]
                    return hislist

        elif(cnnmod.startswith('2r')):
            print('| --- Fit - 2 resolution U-Net Model')
            if extdataset:
                newX, newy = npu.extenddataset(X[idsamples, :, :, :], y[idsamples], transf=extdataset)
            else:
                newX, newy = X[idsamples, :, :, :], y[idsamples]
            newylr = skimage.measure.block_reduce(newy, (1,4,4,1), np.sum) # Compute sum in 4x4 blocks
            newy = [newy, newylr]

            return cnnobj.fit(newX, newy, epochs=epochs, batch_size=batchsize)
            # return cnnobj.fit(newX, newy, epochs=epochs, batch_size=batchsize, callbacks=get_callbacks())

    else:
        print('Fit CNN - Unknown model')
"""
def predict(mod, X):
    newX = X.reshape((-1, X.shape[2]))
    pred = mod.predict(newX)
    # pred = np.exp(pred)-1
    pred = pred.reshape(X.shape[0], X.shape[1])
    return [pred]

def predictM(mod, X, attr_value):
    newX = X.reshape((-1, X.shape[2]))
    pred = mod.predict(newX)
    # pred = np.exp(pred)-1
    pred = pred.reshape(X.shape[0], X.shape[1], len(attr_value)) #HER IT NEED TO PASS len(attr_value)
    predlist = np.dsplit(pred, len(attr_value))
    return predlist #[pred]

def predictloop(cnnmod, patches, batchsize):
    # Custom batched prediction loop
    final_shape = [patches.shape[0], patches.shape[1], patches.shape[2], 1]
    y_pred_probs = np.empty(final_shape,
                            dtype=np.float32)  # pre-allocate required memory for array for efficiency

    # Array with first number for each batch
    batch_indices = np.arange(start=0, stop=patches.shape[0], step=batchsize)  # row indices of batches
    batch_indices = np.append(batch_indices, patches.shape[0])  # add final batch_end row

    i=1
    for index in np.arange(len(batch_indices) - 1):
        batch_start = batch_indices[index]  # first row of the batch
        batch_end = batch_indices[index + 1]  # last row of the batch

        # y_pred_probs[batch_start:batch_end] = cnnmod.predict_on_batch(patches[batch_start:batch_end])
        # y_pred_probs[batch_start:batch_end] = np.expand_dims(
        #     cnnmod.predict_on_batch(patches[batch_start:batch_end])[:,:,:,0], axis=3)

        # Alterado

        # Replace NANs in patches by zero
        ctignore = np.isnan(patches[batch_start:batch_end])
        patchespred = patches[batch_start:batch_end].copy()
        patchespred[ctignore] = 0

        y_pred_probs[batch_start:batch_end] = np.expand_dims(
            np.mean(cnnmod.predict_on_batch(patchespred), axis=3), axis=3)

        # Replace original NANs with NAN
        patchespred[ctignore] = np.nan

        i = i+1
        if(i%1000 == 0): print('»» Batch', i, '/', len(batch_indices), end='/r')

    return y_pred_probs

"""
def predictcnn(obj, mod, fithistory, casestudy, ancpatches, dissshape, batchsize, stride=1):
    if mod == 'lenet':
        print('| --- Predicting new values, Le-Net')
        predhr = obj.predict(ancpatches, batch_size=batchsize, verbose=1)
        predhr = predhr.reshape(dissshape)
        return [predhr]

    elif mod == 'vgg':
        print('| --- Predicting new values, VGG-Net')
        predhr = obj.predict(ancpatches, batch_size=batchsize, verbose=1)
        predhr = predhr.reshape(dissshape)
        return [predhr]

    elif mod == 'uenc':
        print('| --- Predicting new values, U-Net encoder')
        predhr = obj.predict(ancpatches, batch_size=batchsize, verbose=1)
        predhr = predhr.reshape(dissshape)
        return [predhr]

    elif mod.endswith('unet'):
        if(mod == 'unet'):
            if len(fithistory) > 1:
                print('| --- Predicting new patches from several models, 1 resolution U-Net')
                predhr = []
                for i in range(len(fithistory)):
                    obj.load_weights('snapshot_' + casestudy + '_' + str(i) + '.h5')
                    predhr.append(obj.predict(ancpatches, batch_size=batchsize, verbose=1))
                print('| ---- Reconstructing HR images from patches..')
                for i in range(len(predhr)): predhr[i] = ku.reconstructpatches(predhr[i], dissshape, stride)
                return predhr
            else:
                print('| --- Predicting new patches, 1 resolution U-Net')
                predhr = predictloop(obj, ancpatches, batchsize=batchsize)

                print('| ---- Reconstructing HR image from patches..')
                predhr = ku.reconstructpatches(predhr, dissshape, stride)
                # predhr = np.exp(predhr)-1

                return [predhr]
                # # Including variance
                # return [[predhr[0]], predhr[1]]

        elif mod.startswith('2r'):
            print('| --- Predicting new patches, 2 resolution U-Net')
            predhr = obj.predict(ancpatches, batch_size=batchsize, verbose=1)[0]
            print('| ---- Reconstructing HR image from patches..')
            predhr = ku.reconstructpatches(predhr, dissshape, stride)
            return predhr

    else:
        print('Predict CNN - Unknown model')
"""

