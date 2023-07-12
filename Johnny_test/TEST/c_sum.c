#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <float.h>

#if defined(_WIN32)
#  define DLL00_EXPORT_API __declspec(dllexport)
#else
#  define DLL00_EXPORT_API
#endif

#define ELEMENT_TYPE double

#if defined(__cplusplus)
extern "C" {
#endif

DLL00_EXPORT_API ELEMENT_TYPE* pointwiseDistance(const ELEMENT_TYPE *pMatP, size_t rows_p, size_t cols_p,
                                                 const ELEMENT_TYPE *pMatQ, size_t rows_q, size_t cols_q);
DLL00_EXPORT_API int* binaryMaskGenerator(const ELEMENT_TYPE *pMatP, size_t rows_p, size_t cols_p, 
                                                   const ELEMENT_TYPE *pMatGrid, size_t rows_grid, size_t cols_grid);

DLL00_EXPORT_API void deallocArray(ELEMENT_TYPE *pMat);

#if defined(__cplusplus)
}
#endif


ELEMENT_TYPE* pointwiseDistance(
    const ELEMENT_TYPE *pMatP,
    size_t rows_p,
    size_t cols_p,
    const ELEMENT_TYPE *pMatQ,
    size_t rows_q,
    size_t cols_q)
{
    //get all points
    ELEMENT_TYPE * pRet = (ELEMENT_TYPE *)malloc(sizeof(double) * (rows_p + 0));
    
    // get one point
    //ELEMENT_TYPE * pRet = (double *)malloc(sizeof(double) * 1);
    ELEMENT_TYPE tmp_dist = 0;
    ELEMENT_TYPE tmp_sum = 0;
    ELEMENT_TYPE glob_max = 0;
    ELEMENT_TYPE tmp_min = DBL_MAX;

    
    //Loop through each row in P
    for (size_t p = 0; p < rows_p; ++p)
    {
        //printf("P LOOP: %zu \n",p);
        
        //Loop through each row in Q
        for (size_t q = 0; q < rows_q; ++q)
        {
            //printf("Q LOOP: %zu \n",q);
            
            //Loop through each axis x,y,z
            tmp_sum = 0;
            for (size_t axis = 0; axis < cols_p; ++axis)
            {
                //point distance
                tmp_dist = pMatP[p * cols_p + axis] - pMatQ[q * cols_q + axis];
                tmp_dist = tmp_dist * tmp_dist;
                tmp_sum += tmp_dist;
                
                //tmp_sum += (pMatP[p * cols_p + axis] - pMatQ[q * cols_q + axis]) * (pMatP[p * cols_p + axis] - pMatQ[q * cols_q + axis]);
                //printf("tmp_dist: %3.3f \n",tmp_dist);
                
            }
            //if(tmp_sum < glob_max)
            //{
            //    break;
            //}
            //printf("tmp_sum: %3.3f \n", tmp_sum);
            
            //choose minimum
            if (tmp_sum < tmp_min)
            {
                //tmp_min = sqrt(tmp_sum);
                tmp_min = tmp_sum;
            }
        }

        //choose maximum
        //if (tmp_min > glob_max)
        //{

            //get all points
            //tmp_min = sqrt(tmp_sum);
            
            
            //get one point
            //glob_max = tmp_min;
        //}
        //printf("----- MIN: %3.3f-----------\n",tmp_min);

        //get all points
        pRet[p] = sqrt(tmp_min);
        //if ( (tmp_min >=glob_max) && (tmp_min >=glob_max))
        //{
        //    glob_max = tmp_min;
        //}
        tmp_min = DBL_MAX;
        
    }

    //get one point
    //pRet[0] = sqrt(glob_max);
    return pRet;
}




int* binaryMaskGenerator(const ELEMENT_TYPE *pMatP, size_t rows_p, size_t cols_p, 
                                  const ELEMENT_TYPE *pMatGrid, size_t rows_grid, size_t cols_grid)
{
    //init array
    int* pgrid_dist = (int *)malloc(sizeof(int) * (rows_grid + 0));
    for (int g = 0; g < rows_grid; g++)
    {
        pgrid_dist[g] = 0;
    }

    ELEMENT_TYPE tmp_dist = 0;
    ELEMENT_TYPE tmp_sum = 0;

    int tmp_min_g = 0;
    ELEMENT_TYPE tmp_min = DBL_MAX;


    //Loop through each row in P
    for (size_t p = 0; p < rows_p; ++p)
    {
        //printf("P LOOP: %zu \n",p);
        
        //Loop through each row in Grid
        for (size_t g = 0; g < rows_grid; ++g)
        {
            //printf("Q LOOP: %zu \n",q);
            
            //Loop through each axis x,y,z
            tmp_sum = 0;
            for (size_t axis = 0; axis < cols_p; ++axis)
            {
                //point distance
                tmp_dist = pMatP[p * cols_p + axis] - pMatGrid[g * cols_grid + axis];
                tmp_dist = tmp_dist * tmp_dist;
                tmp_sum += tmp_dist;
            }
            //choose minimum
            if (tmp_sum < tmp_min)
            {
                //tmp_min = sqrt(tmp_sum);
                tmp_min = tmp_sum;
                tmp_min_g = g;
            }
        }
        //set value
        pgrid_dist[tmp_min_g] ++;
        tmp_min = DBL_MAX;
    }
    return pgrid_dist;
}






void deallocArray(ELEMENT_TYPE *pMat)
{
    if (pMat)
        free(pMat);
}



