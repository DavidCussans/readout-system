clearvars
% LXtalk device  
% distv1 =10; heigthv1 = 0.0023; widthv1 = 5;offset1=-.0009;
% std 
distv1 =10; heigthv1 = 0.0023; widthv1 = 5;offset1=-.00;
distv2 =10; heigthv2 =heigthv1*1; widthv2 = widthv1;offset2=0;
coincetime=2;
Bandwith=20;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%Connect to oscilloscpe%%%%%%%%%%%%%%%%%%%%%%%%%
MaxNumberPoint = 5000000;       


 load('data_20160126_1654.mat','MV1','MV2','DateString','offset1','offset2');


nrthloops =35;
for thlp=1 : nrthloops
    th1(thlp)=((7+thlp)/9)  * heigthv1;
    th2(thlp)=((7+thlp)/9)* heigthv2;
end

for thlp=1 : nrthloops
    nrs_of_pksv1=0;
    nrs_of_pksv2=0;
    for cnt=1 :length( MV1) 
        if  MV1(cnt) > th1(thlp)
                    nrs_of_pksv1=nrs_of_pksv1+1;
        end  
    
        if MV2(cnt) > th2(thlp)
                    nrs_of_pksv2=nrs_of_pksv2+1;
        end    
   
    end
all_nrs_of_pksv1(thlp)=nrs_of_pksv1;all_nrs_of_pksv2(thlp)=nrs_of_pksv2;
end

fprintf('time string  %s\n\rresults:\n',DateString);

for thlp=1 : nrthloops
   fprintf('cnt %d , thv1 %f, thv2 %f, nrpk1 %d ,nrpk1 %d  \n'  , thlp,1000*th1(thlp),1000*th2(thlp), all_nrs_of_pksv1(thlp),all_nrs_of_pksv2(thlp));
    
end
    
