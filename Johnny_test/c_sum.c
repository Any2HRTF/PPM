#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <limits.h>
#include <float.h>

float * c_sum(const float * matrix, int n, int m)
{
    float * results = (float *)malloc(sizeof(float) * 3*n);
    for (int i = 0;i < 3*n;i++)
    {
        results[i] = matrix[i];
    }
    return results;
}

double * hausdorff_dist(const double * P, const double * Q, int len_P, int len_Q)
{
    double * result = (double *)malloc(sizeof(double) * len_P);
    double tmp_dist = 0;
    double tmp_sum = 0;
    double tmp_min = DBL_MAX;
    result[0]=P[2];
    return result;
}
    /*
    //Loop through each row in P
    for(int p = 0; p < len_P; p++)
    {
        
        //Loop through each row in Q
        for(int q = 0; q < len_Q; q++)
        {
            tmp_sum = 0;
            //Loop through each axis x,y,z
            for(int axis = 0; axis < 3; axis++)
            {
                //point distance
                tmp_dist = P[(p-1)*3 + axis] - Q[(q-1)*3 + axis];
                tmp_dist = tmp_dist * tmp_dist;
                tmp_sum = tmp_sum + tmp_dist;
            }
            //choose minimum
            if (tmp_sum < tmp_min)
            {
                tmp_min = sqrt(tmp_sum);
            }
        }
        result[p] = tmp_min;
        tmp_min = DBL_MAX;
    }
    return result;

*/




/*
int index = 0;
for(int i=0; i< n*m; i+=n){
    results[index] = 0;
    for(int j=0; j<m; j++){
        results[index] += matrix[i+j];
    }
    index += 1;
}
return results;
*/
//}