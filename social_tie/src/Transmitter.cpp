#include "Transmitter.h"

DataSet* Transmitter::AssignJobs(GlobalDataSet* g_dataset, int num_procs)
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
//    for (int p = 1; p < num_procs; p ++)
  //      MPI_Send(&max_space, 1, MPI_INT, p, MSG_SPACE_SIZE, MPI_COMM_WORLD);

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

//       MPI_Send(mem, mem_p, MPI_BYTE, p, MSG_DATA, MPI_COMM_WORLD);        
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

DataSet* Transmitter::GetJobs()
{
//   MPI_Status status;
    int max_space;
    
 //   MPI_Recv(&max_space, 1, MPI_INT, 0, MSG_SPACE_SIZE, MPI_COMM_WORLD, &status);

    char* mem = new char[max_space];
    int mem_p = 0;

//   MPI_Recv(mem, max_space, MPI_BYTE, 0, MSG_DATA, MPI_COMM_WORLD, &status);
    
    DataSet* dataset = new DataSet();
    dataset->num_sample = ReadInt(mem, mem_p);    
    dataset->num_label = ReadInt(mem, mem_p);
    dataset->num_attrib_type = ReadInt(mem, mem_p);
    dataset->num_edge_type = ReadInt(mem, mem_p);
    
    dataset->sample.resize( dataset->num_sample );

    for (int i = 0; i < dataset->num_sample; i ++)
    {
        DataSample* p_sample = new DataSample();
        dataset->sample[i] = p_sample;

        p_sample->num_node = ReadInt(mem, mem_p);
        p_sample->num_edge = ReadInt(mem, mem_p);

        p_sample->node.resize( p_sample->num_node );
        p_sample->edge.resize( p_sample->num_edge );

        for (int t = 0; t < p_sample->num_node; t ++)
        {
            DataNode* p_node = new DataNode();
            p_sample->node[t] = p_node;

            p_node->label = ReadInt(mem, mem_p);
            p_node->num_attrib = ReadInt(mem, mem_p);

            p_node->attrib.resize( p_node->num_attrib );
            p_node->value.resize( p_node->num_attrib );

            for (int k = 0; k < p_node->attrib.size(); k ++)
            {
                p_node->attrib[k] = ReadInt(mem, mem_p);
                p_node->value[k] = ReadDouble(mem, mem_p);
            }
        }

        for (int t = 0; t < p_sample->num_edge; t ++)
        {
            DataEdge* p_edge = new DataEdge();
            p_sample->edge[t] = p_edge;
            p_edge->a = ReadInt(mem, mem_p);
            p_edge->b = ReadInt(mem, mem_p);
            p_edge->edge_type = ReadInt(mem, mem_p);
        }
    }

    return dataset;
}

void Transmitter::Master_SendDoubleArray(double* arr, int n, int num_procs)
{
 //   for (int p = 1; p < num_procs; p ++)
  //      MPI_Send(arr, n * sizeof(double), MPI_BYTE, p, MSG_DOUBLE_ARR, MPI_COMM_WORLD);
}

void Transmitter::Master_CollectGradientInfo(double* gradient, double* f, int num_feature, double* tmp_store, int num_procs)
{
//    MPI_Status status;
    for (int p = 1; p < num_procs; p ++)
    {
  //      MPI_Recv(tmp_store, (num_feature + 1) * sizeof(double), MPI_BYTE, p, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
        *f += tmp_store[ num_feature ];
        for (int i = 0; i < num_feature; i ++)
            gradient[i] += tmp_store[i]; 
    }
}
void Transmitter::Master_SendQuit(int num_procs)
{
    double v = 0.0;
//    for (int p = 1; p < num_procs; p ++)
  //      MPI_Send(&v, sizeof(double), MPI_BYTE, p, MSG_QUIT, MPI_COMM_WORLD);
}

bool Transmitter::Slave_RecvDoubleArray(double* arr, int n)
{
//    MPI_Status status;
  //  MPI_Recv(arr, sizeof(double) * n, MPI_BYTE, 0, MPI_ANY_TAG, MPI_COMM_WORLD, &status);
    
	return false;
    //return (status.MPI_TAG == MSG_QUIT);
}

void Transmitter::Slave_SendGradientInfo(double* gradient, double* f, int num_feature)
{
    gradient[num_feature] = *f;
//    MPI_Send(gradient, (num_feature + 1) * sizeof(double), MPI_BYTE, 0, MSG_DOUBLE_ARR, MPI_COMM_WORLD);
}