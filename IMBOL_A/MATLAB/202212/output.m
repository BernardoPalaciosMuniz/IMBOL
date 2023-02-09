makeoutput(Hmm,Pmbar,T_needleC,T_resC,T_surfC,Dd,U,D_f,D_b,imfiles_f,imfiles_b,fps,startframe,impactframe,endframe)
system('python3 /Users/bernardo/Bernardo_Local/GIT/IMBOL/MATLAB/202212/appendresults')




function makeoutput(Hmm,Pmbar,T_needleC,T_resC,T_surfC,Dd,U,D_f,D_b,imfiles_f,imfiles_b,fps,startframe,impactframe,endframe)
    rho=1400;
    sigma=12.4e-3;
    
    
    folder_f=extractAfter(imfiles_f(1),'/Volumes/IMBOL_A/');
    folder_f=split(folder_f,'/');
    folder_f=join(folder_f(1:3),'/');
    
    
    folder_b=extractAfter(imfiles_b(1),'/Volumes/IMBOL_A/');
    folder_b=split(folder_b,'/');
    folder_b=join(folder_b(1:3),'/');
    
   
    hfg=142e03;
    cp=1300;
    
    t=0:length(D_b)-1;
    t=t'./fps;
    T = array2table([t,D_b]);
    T.Properties.VariableNames(1:2) = {'t [s]','D [m]'};
    folder_b=replace(folder_b,'/','__');
    writetable(T,'Dvst/'+folder_b+'_Dvst.csv','Delimiter',',');
    
    [Dmax_b,I_b]=max(smooth(D_b));
    t_b=t(I_b);
    
    
    t=0:length(D_f)-1;
    t=t'./fps;
    T = array2table([t,D_f]);
    T.Properties.VariableNames(1:2) = {'t [s]','D [m]'};
    folder_f=replace(folder_f,'/','__');
    writetable(T,'Dvst/'+folder_f+'_Dvst.csv','Delimiter',',');
    
    [Dmax_f,I_f]=max(smooth(D_f));
    t_f=t(I_f);
    
    We=rho*U^2*Dd/sigma;
    Ja=cp(T_surfC-T_resC)/hfg;

 
    T = cell2table({Hmm,Pmbar,T_needleC,T_resC,T_surfC,Dd,U,We,Ja,Dmax_b,Dmax_f,t_b,t_f,folder_b,folder_f,startframe,impactframe,endframe});
    T.Properties.VariableNames(1:18) = {'Hmm','Pmbar','T_needleC','T_resC','T_surfC','D_d [m]','U [m/s]','We','Ja','Dmax_b','Dmax_f','tmax_b','tmax_f','source_b','source_f','startframe','impactframe','endframe'};
    writetable(T,'Results_temp.csv','Delimiter',',');
    
    
    

end