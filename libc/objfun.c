#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int K = 3;             // problem dimension (default is 3)

double distance(int i,int j,double **X)
{
   int k;
   double tmp,val;

   val = X[0][j] - X[0][i];  val = val*val;
   for (k = 1; k < K; k++)
   {
      tmp = X[k][j] - X[k][i];  tmp = tmp*tmp;
      val = val + tmp;
   };
   return sqrt(val);
};

double objfun(int n,double **X,int m,double *y,int *u,int *v,double *prior)
{
   int j;
   double term;
   double sigma = 0.0;

   for (j = 0; j < m; j++)
   {
      term = distance(u[j],v[j],X) - y[j];
      term = term*term;
      term = prior[j]*term;
      sigma = sigma + term;
   };

   return sigma;
};

void gradient(int n,double **X,int m,double *y,int *u,int *v,double *prior,double **gX,double *gy,double *memory)
{
   int i,j,k;
   double tmp;

   // cleaning memory space
   for (i = 0; i < n; i++)  memory[i] = 0.0;

   // initialization for gX
   for (k = 0; k < K; k++)
   {
      for (i = 0; i < n; i++)
      {
         gX[k][i] = 0.0;
      }
   };

   // computation of gy and gX (compact form, all steps in one, except case u==v)
   for (j = 0; j < m; j++)
   {
      tmp = distance(u[j],v[j],X);
      gy[j] = -2.0*prior[j]*(tmp - y[j]);
      if (tmp > 0.0)
      {
         tmp = -prior[j]*y[j]/tmp;
         memory[u[j]] = memory[u[j]] + prior[j] + tmp;
         memory[v[j]] = memory[v[j]] + prior[j] + tmp;
         tmp = 2.0*(-prior[j] - tmp);
         for (k = 0; k < K; k++)
         {
            gX[k][u[j]] = gX[k][u[j]] + tmp*X[k][v[j]];
            gX[k][v[j]] = gX[k][v[j]] + tmp*X[k][u[j]];
         };
      };
   };

   // completing the computation of gX (case u==v)
   for (k = 0; k < K; k++)
   {
      for (i = 0; i < n; i++)
      {
         gX[k][i] = gX[k][i] + 2.0*memory[i]*X[k][i];
      };
   };

   //////// TEST
   /*
   for (k = 0; k < K; k++)
   {
      for (i = 0; i < n; i++)
      {
         X[k][i] = X[k][i] + 1e-15;
         gX[k][i] = objfun(n,X,m,y,u,v,prior);
         X[k][i] = X[k][i] - 2e-15;
         gX[k][i] = gX[k][i] - objfun(n,X,m,y,u,v,prior);
         X[k][i] = X[k][i] + 1e-15;
         gX[k][i] = gX[k][i]/2e-15;
      };
   };
   */
};
