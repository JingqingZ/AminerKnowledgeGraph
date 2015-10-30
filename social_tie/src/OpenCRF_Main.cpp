#include "Config.h"
#include "DataSet.h"
#include "CRFModel.h"
#include <stdlib.h>

/*
void DEBUG__AddLinearEdge(DataSet* dataset)
{
    int n = dataset->num_sample;
    for (int i = 0; i < n; i ++)
    {
        DataSample *sample = dataset->sample[i];        
        sample->edge.clear();
        for (int j = 1; j < sample->num_node; j ++)
        {
            {
                DataEdge *e = new DataEdge();
                e->a = j - 1; e->b = j; e->edge_type = 0;
                sample->edge.push_back( e );
            }
        }
        sample->num_edge = sample->edge.size();
    }
    dataset->num_edge_type = 1;
}
*/

void MakeEvaluate(Config* conf, GlobalDataSet* g_dataset, CRFModel* model)
{
    if (conf->my_rank == 0)
    {
        GlobalDataSet* g_testdata = new GlobalDataSet();
        DataSet* testdata = new DataSet();        

        g_testdata->LoadDataWithDict(conf->test_file.c_str(), conf, g_dataset->label_dict, g_dataset->attrib_dict, g_dataset->edge_type_dict);
        testdata->sample = g_testdata->sample;
        testdata->num_sample = g_testdata->sample.size();
        testdata->num_edge_type = g_testdata->num_edge_type;
        testdata->num_attrib_type = g_testdata->num_attrib_type;
        testdata->num_label = g_testdata->num_label;

        for (int i = 0; i < testdata->num_sample; i ++)
        {        
            testdata->sample[i]->num_node = testdata->sample[i]->node.size();
            testdata->sample[i]->num_edge = testdata->sample[i]->edge.size();        

            for (int t = 0; t < testdata->sample[i]->num_node; t ++)
                testdata->sample[i]->node[t]->num_attrib = testdata->sample[i]->node[t]->attrib.size();
        }

        //DEBUG__AddLinearEdge(testdata);

        model->InitEvaluate(conf, testdata);
        model->Evalute();
    }
}

void WriteInt(char* mem, int& mem_p, int v)
{
    *((int*)(mem + mem_p)) = v;
    mem_p += sizeof(int);
}

void WriteDouble(char* mem, int& mem_p, double v)
{
    *((double*)(mem + mem_p)) = v;
    mem_p += sizeof(double);
}

int ReadInt(char* mem, int& mem_p)
{
    int v = *((int*)(mem + mem_p));
    mem_p += sizeof(int);
    return v;
}

double ReadDouble(char* mem, int& mem_p)
{
    double v = *((double*)(mem + mem_p));
    mem_p += sizeof(double);
    return v;
}


DataSet* AssignJobs(GlobalDataSet* g_dataset, int num_procs)
{
    int tot_sample = g_dataset->sample.size();    
    int avg_sample = tot_sample / num_procs;

    // Assign Jobs
    int* start = new int[num_procs + 1];
    for (int i = 0; i < num_procs; i ++)
        start[i] = i * avg_sample;
    start[num_procs] = tot_sample;

    // Calc the maximum buffer size
    int max_space = 0;
    int curt_space;
    for (int p = 1; p < num_procs; p ++)
    {
        curt_space = 0;
        for (int i = start[p]; i < start[p + 1]; i ++)
            curt_space += g_dataset->sample[i]->GetSize();
        if (curt_space > max_space)
            max_space = curt_space;
    }
    max_space += 1024;

    // Send the buffer size
    //for (int p = 1; p < num_procs; p ++)
    //    MPI_Send(&max_space, 1, MPI_INT, p, MSG_SPACE_SIZE, MPI_COMM_WORLD);

    char *mem = new char[max_space];
    int mem_p;

    for (int p = 1; p < num_procs; p ++)
    {
        mem_p = 0;
        WriteInt(mem, mem_p, start[p + 1] - start[p]);        

        WriteInt(mem, mem_p, g_dataset->num_label);
        WriteInt(mem, mem_p, g_dataset->num_attrib_type);
        WriteInt(mem, mem_p, g_dataset->num_edge_type);

        for (int i = start[p]; i < start[p + 1]; i ++)
        {
            DataSample* p_sample = g_dataset->sample[i];

            p_sample->num_node = p_sample->node.size();
            p_sample->num_edge = p_sample->edge.size();
            WriteInt(mem, mem_p, p_sample->num_node);
            WriteInt(mem, mem_p, p_sample->num_edge);

            for (int t = 0; t < p_sample->num_node; t ++)
            {
                DataNode* p_node = p_sample->node[t];
                p_node->num_attrib = p_node->attrib.size();
                WriteInt(mem, mem_p, p_node->label);
                WriteInt(mem, mem_p, p_node->num_attrib);

                for (int k = 0; k < p_node->attrib.size(); k ++)
                {
                    WriteInt(mem, mem_p, p_node->attrib[k]);
                    WriteDouble(mem, mem_p, p_node->value[k]);
                }
            }

            for (int t = 0; t < p_sample->num_edge; t ++)
            {
                DataEdge* p_edge = p_sample->edge[t];
                WriteInt(mem, mem_p, p_edge->a);
                WriteInt(mem, mem_p, p_edge->b);
                WriteInt(mem, mem_p, p_edge->edge_type);
            }

            delete p_sample;
            g_dataset->sample[i] = NULL;
        }

        //MPI_Send(mem, mem_p, MPI_BYTE, p, MSG_DATA, MPI_COMM_WORLD);        
    }

    DataSet* dataset = new DataSet();
    dataset->num_sample = start[1];    
    dataset->num_label = g_dataset->num_label;
    dataset->num_attrib_type = g_dataset->num_attrib_type;
    dataset->num_edge_type = g_dataset->num_edge_type;

    dataset->sample.resize( dataset->num_sample );
    for (int i = 0; i < start[1]; i ++)
    {
        dataset->sample[i] = g_dataset->sample[i];
        dataset->sample[i]->num_node = dataset->sample[i]->node.size();
        dataset->sample[i]->num_edge = dataset->sample[i]->edge.size();        

        for (int t = 0; t < dataset->sample[i]->num_node; t ++)
            dataset->sample[i]->node[t]->num_attrib = dataset->sample[i]->node[t]->attrib.size();
    }

    return dataset;
}


void Estimate(Config* conf)
{
    GlobalDataSet* g_dataset;
    DataSet* dataset;

    if (conf->my_rank == 0) // master
    {
        g_dataset = new GlobalDataSet();
        g_dataset->LoadData(conf->train_file.c_str(), conf);
        g_dataset->label_dict.SaveMappingDict(conf->dict_file.c_str());

		dataset = AssignJobs(g_dataset, conf->num_procs);
        // Assign jobs
        //dataset = Transmitter::AssignJobs(g_dataset, conf->num_procs);
    }
    else
    {
        // Get jobs
        //dataset = Transmitter::GetJobs();
    }

    printf("num_label = %d\n", dataset->num_label);
    printf("num_sample = %d\n", dataset->num_sample);
    printf("num_edge_type = %d\n", dataset->num_edge_type);
    printf("num_attrib_type = %d\n", dataset->num_attrib_type);

    CRFModel *model = new CRFModel();
    
    model->InitTrain(conf, dataset);    
    model->Train();
    
    if (conf->my_rank == 0)
        model->SaveModel(conf->dst_model_file.c_str());
      
    MakeEvaluate(conf, g_dataset, model);
}

void EstimateContinue(Config* conf)
{
    GlobalDataSet* g_dataset;
    DataSet* dataset;

    if (conf->my_rank == 0) // master
    {
        g_dataset = new GlobalDataSet();
        g_dataset->LoadData(conf->train_file.c_str(), conf);
        g_dataset->label_dict.SaveMappingDict(conf->dict_file.c_str());

		dataset = AssignJobs(g_dataset, conf->num_procs);
        // Assign jobs
        //dataset = Transmitter::AssignJobs(g_dataset, conf->num_procs);
    }
    else
    {
        // Get jobs
        //dataset = Transmitter::GetJobs();
    }

    //DEBUG__AddLinearEdge(dataset);

    printf("num_label = %d\n", dataset->num_label);
    printf("num_sample = %d\n", dataset->num_sample);
    printf("num_edge_type = %d\n", dataset->num_edge_type);
    printf("num_attrib_type = %d\n", dataset->num_attrib_type);

    CRFModel *model = new CRFModel();
    
    model->InitTrain(conf, dataset);

    if (conf->my_rank == 0)
        model->LoadModel(conf->src_model_file.c_str());

    model->Train();

    if (conf->my_rank == 0)
        model->SaveModel(conf->dst_model_file.c_str());
    
    MakeEvaluate(conf, g_dataset, model);
}

void Inference(Config* conf)
{
    GlobalDataSet* g_dataset;
    DataSet* dataset;

    if (conf->my_rank == 0) // master
    {
        g_dataset = new GlobalDataSet();
        g_dataset->LoadData(conf->train_file.c_str(), conf);
        g_dataset->label_dict.SaveMappingDict(conf->dict_file.c_str());

		dataset = AssignJobs(g_dataset, conf->num_procs);
        // Assign jobs
        //dataset = Transmitter::AssignJobs(g_dataset, conf->num_procs);
    }
    else
    {
        // Get jobs
       // dataset = Transmitter::GetJobs();
    }

    //DEBUG__AddLinearEdge(dataset);

    printf("num_label = %d\n", dataset->num_label);
    printf("num_sample = %d\n", dataset->num_sample);
    printf("num_edge_type = %d\n", dataset->num_edge_type);
    printf("num_attrib_type = %d\n", dataset->num_attrib_type);

    CRFModel *model = new CRFModel();
    
    model->InitTrain(conf, dataset);
    if (conf->my_rank == 0)
        model->LoadModel(conf->src_model_file.c_str());
    
    MakeEvaluate(conf, g_dataset, model);
}

int main(int argc, char* argv[])
{
    int         my_rank;
    int         num_procs;

    // Initialize MPI environment
	my_rank = 0;
	num_procs = 1;

    // Load Configuartion
    Config* conf = new Config();
    if (! conf->LoadConfig(my_rank, num_procs, argc, argv))
    {
        conf->ShowUsage();
        exit( 0 );
    }

    if (conf->task == "-est")
    {
        Estimate(conf);
    }
    else if (conf->task == "-estc")
    {
        EstimateContinue(conf);
    }
    else if (conf->task == "-inf")
    {
        Inference(conf);
    }
    else
    {
        Config::ShowUsage();
    }
}