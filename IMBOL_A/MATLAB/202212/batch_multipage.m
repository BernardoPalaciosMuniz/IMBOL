explog=uiimport('-file');
explog=struct2table(explog);


home=uigetdir('/Volumes/IMBOL_A');
folders_f=dir([home,'/N7*']);
nfolders=length(folders_f);
H_setmm=explog{:,'H_mm'};
Pmbar=explog{:,'P_mbar'};
T_needleC=explog{:,'Tneedle_C'};
T_resC=explog{:,'Tres_C'};
T_surfC=explog{:,'Tsurf_C'};
D_b=0;
imfiles_b=0;
for i=1:nfolders
    impactframe=impactframelist(i);
    imfiles_f=getImfiles([folders_f(i).folder,'/',folders_f(i).name]);
    loadim_multipage;
    impactspeed;
    spreading;
%     bottom_diameter;
    makeoutput(H_setmm(i),Pmbar(i),T_needleC(i),T_resC(i),T_surfC(i),Dd,U,D_f,D_b,imfiles_f,imfiles_b,fps,startframe,impactframe,endframe)
    system('python3 /Users/bernardo/Bernardo_Local/GIT/IMBOL/MATLAB/202212/appendresults')
    
end


clear('i','nfolders','test')





function files = getImfiles(folder)
imgs=dir([folder,'/*.tif']);
files=string(zeros(length(imgs),1));
for i= 1:length(imgs)
    test=startsWith(imgs(i).name,'.');
    if  ~test
    files(i)=[imgs(i).folder,'/',imgs(i).name];
    end
    
end
files=files(files~=string(0));

end

function makeoutput(Hmm,Pmbar,T_needleC,T_resC,T_surfC,Dd,U,D_f,D_b,imfiles_f,imfiles_b,fps,startframe,impactframe,endframe)
    rho=1400;
    sigma=12.4e-3;
    hfg=142e03;
    cp=1300;
    
    We=rho*U^2*Dd/sigma;
    Ja=cp*(T_surfC-T_resC)/hfg;
   
    folder_f=extractAfter(imfiles_f(1),'/Volumes/IMBOL_A/');
    folder_f=split(folder_f,'/');
    folder_f=join(folder_f(1:3),'/');
    
    
%     folder_b=extractAfter(imfiles_b(1),'/Volumes/IMBOL_A/');
%     folder_b=split(folder_b,'/');
%     folder_b=join(folder_b(1:3),'/');
    
   
    
    
%     t=0:length(D_b)-1;
%     t=t'./fps;
%     T = array2table([t,D_b]);
%     T.Properties.VariableNames(1:2) = {'t [s]','D [m]'};
%     folder_b=replace(folder_b,'/','__');
%     writetable(T,'Dvst/'+folder_b+'_Dvst.csv','Delimiter',',');
%     
%     [Dmax_b,I_b]=max(smooth(D_b));
%     t_b=t(I_b);
    folder_b=0;
    Dmax_b=0;
    t_b=0;

    
    
    t=0:length(D_f)-1;
    t=t'./fps;
    T = array2table([t,D_f]);
    T.Properties.VariableNames(1:2) = {'t [s]','D [m]'};
    folder_f=replace(folder_f,'/','__');
    writetable(T,'Dvst_2209/'+folder_f+'_Dvst.csv','Delimiter',',');
    
    [Dmax_f,I_f]=max(smooth(D_f));
    t_f=t(I_f);
    
    

 
    T = cell2table({Hmm,Pmbar,T_needleC,T_resC,T_surfC,Dd,U,We,Ja,Dmax_b,Dmax_f,t_b,t_f,folder_b,folder_f,startframe,impactframe,endframe});
    T.Properties.VariableNames(1:18) = {'H_mm','P_mbar','Tneedle_C','Tres_C','Tsurf_C','Dd_m','U_m_s','We','Ja','Dmaxb_m','Dmaxf_m','tmaxb_s','tmaxf_s','sourceb','sourcef','startframe','impactframe','endframe'};
    writetable(T,'Results_temp.csv','Delimiter',',');
    
    
    

end