//+------------------------------------------------------------------+
//|                                                  VWAP    EMA.mq5 |
//|                                                  Fudo Capital BV |
//|                                                                  |
//+------------------------------------------------------------------+

#property copyright "Fudo Capital BV"
#include <Trade\Trade.mqh>//Instatiate Trades Execution Library

CTrade trade;



ENUM_TIMEFRAMES Timeframe   = PERIOD_CURRENT;
ENUM_APPLIED_PRICE AppPrice = PRICE_CLOSE;

input group "Trade inputs"
input double ClosePercent       = 50;
input double SlFactor           = 1;    //Reduce o aumenta x distancia el sl
input double TpFactor           = 1;    //Reduce o aumenta x distancia el tp
input double riskPercentage     = 1;    //The percent of equity risked per trade
input double riskRewardTarget   = 2;  //Risk Reward target to close partial
input int minHoldingPeriod      = 0;   // min holding period to close trade partial in days
input int atrPeriod             = 16;

input group "Dinamic risk inputs"
input double delta              = 0.12;
input int option                = 0;

input group "Ema Inputs"
input int fastEmaPeriod         = 1;
input int slowEMAPeriod         = 5;

/*input group "ADX input"
input int adxPeriod             = 14;
*/
input group "Indicators inputs"
input int vwapZoneMultiplyer    = 2;    //PIPS
input int switchCandelCondition = 0;  // nomber of candels to validate a vwap

input group "Equity managment imputs"
input double maxDrowdown        = 100;  // Porcentaje maximo de drowdown
input double maxDrowdownAnual   = 100;  // Porcentaje maximo de drowdown anual
input double maxDrowdownMonthly = 100;  // Porcentaje maximo de drowdown mensual
input double maxDrowdownDaily   = 15;   // Porcentaje maximo de drowdown diario
input double TargetAnualy       = 80;  // Target anual no se usa todavia
input double TargetMonthly      = 80;  // Target mensual no se usa todavia
input double TargetDaily        = 20;  // Target semanal no se usa todavia

bool partialCondition         = true;
//Total decimal for the a point
double point                =SymbolInfoDouble(_Symbol,SYMBOL_POINT);



int barsTotal;
bool firstPivot=false;

datetime pivotTime;
//anchored vwaps handles
int handleVWAP;
//Emas handle
int handleFastEMA;
int handleSlowEMA;
// ATR handel
int handelATR;
/*/ADX handel
int handelADX;*/
ENUM_APPLIED_PRICE AppPriceVWAP;

double slowEMA[],fastEMA[];
double VWAP[],N1[],N2[],N3[],N4[],N5[];
double ATR[];

double SLPrice;

//Bool conditions  to find the first pivot
bool firstCross=false;
bool firstCrossUnder=false;
bool firstCrossOver=false;
bool N5trade=false;
bool N4trade=false;
bool N3trade=false;
bool N2trade=false;
bool N1trade=false;

int firstCrossShift;
datetime firstCrossTime;
datetime crossTime;

//Equity global variables
double EquityStart;
double EquityYear ;
double EquityMonth;
double EquityDay ;
int Year;
int Month;
int DayOfYear;
int startWeek;

datetime StartTime;

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+


//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+


// Esta funcion genera un alpfa tal que al aumentar el alpha ariesgas menos por cada operacion
// el delta determina la velocidad con la que aproxima a invertir practicamente 0,mientras mayor sea mas rapido converge a ariesgar cero en la operacon
//
double DynamicRiskAlpha(double deltaValue, int vwapTime, int Option)
  {
   double y;
   if(Option==1)
     {
      y=1.4+MathArctan(deltaValue*vwapTime-5.8);
      if(NormalizeDouble(y/3,2)==1)
         return (0.99);
      return(NormalizeDouble(y/3,2));
     }
   if(Option==2)
     {
      y=1+MathSin(deltaValue*vwapTime-1.57);
      if(vwapTime<MathSin(1)/deltaValue)
         return(NormalizeDouble(y/2,2));
      else
         return(0.99);

     }
   return(0);
  }


//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
double PointValue(string symbol)
  {
   double tickSize      =SymbolInfoDouble(symbol,SYMBOL_TRADE_TICK_SIZE);
   double tickValue     =SymbolInfoDouble(symbol,SYMBOL_TRADE_TICK_VALUE);

   double ticksPerPoint =tickSize/point;
   double pointValue    =tickValue/ticksPerPoint;

   return(pointValue);

  }

// Calculating specific Lots for a trade function
double Lots(string symbol,double riskAmount,double riskPoints)
  {
//Print(riskAmount);
   double pointValue = PointValue(symbol);
   double totalLots=NormalizeDouble(riskAmount/(pointValue*riskPoints),2);
//PrintFormat("riskAmount = %f || totalLots= %f",riskAmount,totalLots);
   double min_volume=SymbolInfoDouble(Symbol(),SYMBOL_VOLUME_MIN);
   double max_volume=SymbolInfoDouble(Symbol(),SYMBOL_VOLUME_MAX);

   if(totalLots<min_volume)
      return(min_volume);
   if(totalLots>max_volume)
      return(max_volume);
   else
      return(totalLots);

  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
double RiskAmount(string symbol, double riskPoints,double riskLots)
  {
   double pointValue = PointValue(symbol);

   double riskAmount  = NormalizeDouble(pointValue*riskLots*riskPoints,3);
   return riskAmount  ;

  }
//Modifies vwap function
bool modifyParametersFile(datetime dateStart, ENUM_APPLIED_PRICE sourcePrice, string fileName)
  {
   int h=FileOpen(fileName,FILE_WRITE|FILE_ANSI|FILE_CSV|FILE_SHARE_WRITE|FILE_SHARE_READ);
   if(h==INVALID_HANDLE)
     {
      Print("Error opening file");
      return false;
     }
   FileWrite(h, TimeToString(dateStart,TIME_DATE|TIME_MINUTES));
   FileWrite(h, sourcePrice);
   FileClose(h);
   return true;
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+


//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
int OnInit()
  {

   firstPivot=false;
   barsTotal=iBars(_Symbol,Timeframe);

   handleFastEMA     = iMA(_Symbol,PERIOD_H1,fastEmaPeriod,1,MODE_EMA, PRICE_WEIGHTED);
   handleSlowEMA     = iMA(_Symbol,PERIOD_H1,slowEMAPeriod,1,MODE_EMA, PRICE_WEIGHTED);

   handelATR         = iATR(_Symbol,PERIOD_CURRENT,atrPeriod);

//handelADX         = iADX(_Symbol,PERIOD_CURRENT,adxPeriod);

   EquityStart       = AccountInfoDouble(ACCOUNT_EQUITY);
   EquityYear        = AccountInfoDouble(ACCOUNT_EQUITY);
   EquityMonth       = AccountInfoDouble(ACCOUNT_EQUITY);
   EquityDay         = AccountInfoDouble(ACCOUNT_EQUITY);

   StartTime         = TimeLocal();
   MqlDateTime StartLocalTime;
   TimeToStruct(StartTime,StartLocalTime);

   Year              = StartLocalTime.year;
   Month             = StartLocalTime.mon;
   DayOfYear         = StartLocalTime.day_of_year;



   return(INIT_SUCCEEDED);


  }


//+------------------------------------------------------------------+
//|                                                                  |
//+--------------------------------------------------------------+
void OnDeinit(const int reason)
  {

  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
//Trade Open
bool tradeO=false;
// Lots per trade
double tradeLots[5];

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+

double OnTester(){
   return TpFactor/SlFactor;
   
}
void OnTick()
  {
   datetime localTime         = TimeLocal();
   double totalEquityNow = AccountInfoDouble(ACCOUNT_EQUITY);
   double yearPercent    = ((totalEquityNow/EquityYear)-1)*100;
   double monthPercent   = ((totalEquityNow/EquityMonth)-1)*100;
   double dayPercent   = ((totalEquityNow/EquityDay)-1)*100;
   double overallPercent = ((totalEquityNow/EquityStart)-1)*100;
   int bars=iBars(_Symbol,Timeframe);


 //Cada calculo dentro de este if se hara en el primer tick de una nueva vela

   if(barsTotal<bars)
    {
      tradeO=false;
      //Ema Buffers
      CopyBuffer(handleFastEMA,0,1,2,fastEMA);
      CopyBuffer(handleSlowEMA,0,1,2,slowEMA);
      //VWAP buffers
      CopyBuffer(handleVWAP,0,1,2,VWAP);
      CopyBuffer(handleVWAP,1,1,2,N1);
      CopyBuffer(handleVWAP,2,1,2,N2);
      CopyBuffer(handleVWAP,3,1,2,N3);
      CopyBuffer(handleVWAP,4,1,2,N4);
      CopyBuffer(handleVWAP,5,1,2,N5);
      //ATR buffer
      CopyBuffer(handelATR,0,1,2,ATR);


      string StringComent="Last vwap 0: " + DoubleToString(VWAP[0],_Digits) + "| Last vwap 1: " + DoubleToString(VWAP[1],_Digits)+
                          "\nLast N5 0: " + DoubleToString(N5[0],_Digits) + " | Last N5 1: " + DoubleToString(N5[1],_Digits)+
                          "\n ATR 0: "+DoubleToString(ATR[0],_Digits);

      string equityComment="Yearly P&L : "+DoubleToString(NormalizeDouble(yearPercent,2))+ " % \n"+
                           "Monthly P&L : "+DoubleToString(NormalizeDouble(monthPercent,2))+ " % \n"+
                           " Daily P&L : "+DoubleToString(NormalizeDouble(dayPercent,2))+ " % \n"
                           "Overall P&L : "+DoubleToString(NormalizeDouble(overallPercent,2))+ " % \n";
      Comment(equityComment);
      //Actualizamos el numero total de barras
      barsTotal=bars;



      //Locate first VWAP Pivot
      if(!firstPivot)
        {
         //Para el primer pivote necenitamos encontrar los dos primeros cruces para saber si tomamos un High o un Low
         // Encuentra el primer cruce
         if(!firstCross)
           {

            if(fastEMA[0]>slowEMA[0] && fastEMA[1]<=slowEMA[1]) //first cross under condition
              {

               firstCross=true;
               firstCrossUnder=true;
               firstCrossTime=iTime(_Symbol,Timeframe,1);
               Print("Entra First CrossUnder Time: ", firstCrossTime);

              }
            if(fastEMA[0]<slowEMA[0] && fastEMA[1]>=slowEMA[1]) //first cross over condition
              {
               firstCross=true;
               firstCrossOver=true;
               firstCrossTime=iTime(_Symbol,Timeframe,1);
               Print("Entra First CrossOver Time: ", firstCrossTime);

              }
           }
         //Encuentra el segundo cruce
         //Second cross under after cross over
         if(firstCrossOver && fastEMA[0]>slowEMA[0] && fastEMA[1]<=slowEMA[1])
           {

            firstPivot      = true;
            crossTime       = iTime(_Symbol,Timeframe,1);
            firstCrossShift = iBarShift(_Symbol,Timeframe,firstCrossTime);
            int newShift    = iHighest(_Symbol,Timeframe,MODE_HIGH,firstCrossShift);
            pivotTime       = iTime(_Symbol,Timeframe,newShift);

            AppPriceVWAP    = PRICE_HIGH;
            handleVWAP      = iCustom(_Symbol, Timeframe, "AnchoredVWAP.ex5", pivotTime, AppPriceVWAP);
            Print("Entra Second CrossUnder - PivotTime: ", pivotTime, " AppPrice: ", AppPriceVWAP);

           }
         //Second cross over after cross under
         if(firstCrossUnder && fastEMA[0]<slowEMA[0] && fastEMA[1]>=slowEMA[1])
           {

            firstPivot      = true;
            crossTime       = iTime(_Symbol,Timeframe,1);
            firstCrossShift = iBarShift(_Symbol,Timeframe,firstCrossTime);
            int newShift    = iLowest(_Symbol,Timeframe,MODE_LOW,firstCrossShift);
            pivotTime       = iTime(_Symbol,Timeframe,newShift);

            AppPriceVWAP    = PRICE_LOW;
            handleVWAP      = iCustom(_Symbol, Timeframe, "AnchoredVWAP.ex5", pivotTime, AppPriceVWAP);
            Print("Entra Second CrossOver - PivotTime: ", pivotTime, " AppPrice: ", AppPriceVWAP);
           }
        }
    }
    // Condicion de twist
      double high1=iHigh(_Symbol,Timeframe,0); // Penultimo
      double high0=iHigh(_Symbol,Timeframe,1);// Antepenultimo


      double low1=iLow(_Symbol,Timeframe,0); // Penultimo
      double low0=iLow(_Symbol,Timeframe,1);// Antepenultimo

      if(firstPivot && AppPriceVWAP==PRICE_HIGH && high1>VWAP[1])//  && high0<VWAP[0] && close2>VWAP[2])
        {
         double VWAPTemp[];
         CopyBuffer(handleVWAP,0,1,1,VWAPTemp);
         double prevValue = VWAPTemp[0];
         int prevShift =iBarShift(_Symbol, Timeframe, pivotTime,true);
         int newShift = iLowest(_Symbol,Timeframe,MODE_LOW,prevShift,0);

         if(prevShift != 0)
          pivotTime = iTime(_Symbol,Timeframe,newShift);

         AppPriceVWAP=PRICE_LOW;
         modifyParametersFile(pivotTime, AppPriceVWAP,"parameters.csv");

         //Esperando que el indicador cambie de valores por el modify
         Print("Entra a la verificación del cambio del VWAP");
         MqlDateTime localTimeMql;
         do
           {
            CopyBuffer(handleVWAP,0,1,1,VWAPTemp);
            Sleep(20);
            TimeToStruct(TimeCurrent(),localTimeMql);
           }
         while(prevValue == VWAPTemp[0] && !(localTimeMql.hour>=21 && localTimeMql.day_of_week==5));
         Print("Sale de la verificación del cambio del VWAP");
         CopyBuffer(handleVWAP,0,1,2,VWAP);
         CopyBuffer(handleVWAP,1,1,2,N1);
         CopyBuffer(handleVWAP,2,1,2,N2);
         CopyBuffer(handleVWAP,3,1,2,N3);
         CopyBuffer(handleVWAP,4,1,2,N4);
         CopyBuffer(handleVWAP,5,1,2,N5);
         Print("Modificando pivote PivotTime: ", pivotTime, " AppPrice: ", AppPriceVWAP);
        }

      else
         if(firstPivot && AppPriceVWAP==PRICE_LOW && low1<VWAP[1])// && low0>VWAP[0] && close2<VWAP[2])
           {
            double VWAPTemp[];
            CopyBuffer(handleVWAP,0,1,1,VWAPTemp);
            double prevValue = VWAPTemp[0];
            int prevShift =iBarShift(_Symbol, Timeframe, pivotTime,true);
            int newShift = iHighest(_Symbol,Timeframe,MODE_HIGH, prevShift,0);

            if(prevShift != 0)
              pivotTime = iTime(_Symbol,Timeframe,newShift);

            AppPriceVWAP=PRICE_HIGH;
            modifyParametersFile(pivotTime, AppPriceVWAP,"parameters.csv");
            //Esperando que el indicador cambie de valores por el modify
            Print("Entra a la verificación del cambio del VWAP");
            MqlDateTime localTimeMql;
            do
              {
                CopyBuffer(handleVWAP,0,1,1,VWAPTemp);
                Sleep(20);
                TimeToStruct(TimeCurrent(),localTimeMql);
              }
            while(prevValue == VWAPTemp[0] && !(localTimeMql.hour>=21 && localTimeMql.day_of_week==5));
            Print("Sale de la verificación del cambio del VWAP");
            CopyBuffer(handleVWAP,0,1,2,VWAP);
            CopyBuffer(handleVWAP,1,1,2,N1);
            CopyBuffer(handleVWAP,2,1,2,N2);
            CopyBuffer(handleVWAP,3,1,2,N3);
            CopyBuffer(handleVWAP,4,1,2,N4);
            CopyBuffer(handleVWAP,5,1,2,N5);
            Print("Modificando pivote PivotTime: ", pivotTime, " AppPrice: ", AppPriceVWAP);

           }



      // Condicion de trades

    
    //Aseguramos que N5trade sea false cuando se halla tomado sl o tp del trade
    //+---Idea para las 5 uña es usar los COMENTARIOS como identificador distinto a cada uña ---+

   bool N5in,N4in,N3in,N2in,N1in;
   N5in=false;
   N4in=false;
   N3in=false;
   N2in=false;
   N1in=false;



    //Loop para la modificacion de trades
   for(int i=PositionsTotal()-1; i>=0; i--)
     {
      ulong posTicket=PositionGetTicket(i);

      if(PositionSelectByTicket(posTicket))
        {

         double posTp               = PositionGetDouble(POSITION_TP);
         double PositionSL          = PositionGetDouble(POSITION_SL);
         double positionOpenPrice   = PositionGetDouble(POSITION_PRICE_OPEN);
         double positionProfit      = PositionGetDouble(POSITION_PROFIT);
         double positionLots        = PositionGetDouble(POSITION_VOLUME);

         double lotsToClose         = NormalizeDouble(positionLots*ClosePercent/100,2);

         string commentTrade        = PositionGetString(POSITION_COMMENT);
         ENUM_POSITION_TYPE posType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
         datetime positionOpenTime  = (datetime)PositionGetInteger(POSITION_TIME);



         double pointsToStop;

         if(posType==POSITION_TYPE_BUY)
            pointsToStop=(positionOpenPrice-PositionSL)/point;
         else
            pointsToStop=(PositionSL-positionOpenPrice)/point;

         double RiskOfTrade=RiskAmount(_Symbol,pointsToStop,positionLots);

         MqlDateTime MyOpenTime;
         TimeToStruct(positionOpenTime,MyOpenTime);


         MqlDateTime MyLocalTime;
         TimeToStruct(localTime,MyLocalTime);

         int openHour              = MyOpenTime.hour;
         int openDayOfYear         = MyOpenTime.day_of_year;

         int localMinute           = MyLocalTime.min;
         int localHour             = MyLocalTime.hour;
         int localDay              = MyLocalTime.day;
         int localDayOfYear        = MyLocalTime.day_of_year;
         int localMonth            = MyLocalTime.mon;
         //condicion para terminar el año sin posiciones abiertas ademas que prevee el caso en el cual la diferencia es negativa
         bool newYearCondition= (localMinute== 59 && localHour==23 && localDay==31 && localMonth==12);

         int diference=localDayOfYear-openDayOfYear;
         double riskReward=positionProfit/RiskOfTrade;

         double currentSpread = SymbolInfoInteger(_Symbol,SYMBOL_SPREAD)*point;
   

         if(diference>=minHoldingPeriod && riskReward>riskRewardTarget)
           {

            if(((commentTrade=="N5") || (commentTrade=="N4") || (commentTrade=="N3") || (commentTrade=="N4") || (commentTrade=="N5")) && partialCondition)
              {
               Print("Parcial close Trade: ", commentTrade, " RR: ", riskReward);              
               trade.PositionClosePartial(posTicket,lotsToClose);
               if(posType==POSITION_TYPE_BUY)
                  trade.PositionModify(posTicket,positionOpenPrice+currentSpread,posTp);
               else
                  trade.PositionModify(posTicket,positionOpenPrice-currentSpread,posTp);
              }
           }


         if((AppPriceVWAP==PRICE_HIGH && posType==POSITION_TYPE_BUY)|| (AppPriceVWAP== PRICE_LOW && posType==POSITION_TYPE_SELL) || newYearCondition)
           {
            if(commentTrade=="N5")
               N5trade=false;
            if(commentTrade=="N4")
               N4trade=false;
            if(commentTrade=="N3")
               N3trade=false;
            if(commentTrade=="N2")
               N2trade=false;
            if(commentTrade=="N1")
               N1trade=false;
            trade.PositionClose(posTicket);
            Print("Se ha cerrado la posicion del Nail: ", commentTrade);
           }

         // Verificamos de las posiciones abiertas que uñas tienen posicion abierta

         if(commentTrade=="N5")
            N5in=true;
         if(commentTrade=="N4")
            N4in=true;
         if(commentTrade=="N3")
            N3in=true;
         if(commentTrade=="N2")
            N2in=true;
         if(commentTrade=="N1")
            N1in=true;


        }

     }

    //Verificamos si las posiciones se cerraron por otro motivo distinto al switch comprabando que no este abierta
   
   if(N5trade && !N5in)
      N5trade=false;
   if(N4trade && !N4in)
      N4trade=false;
   if(N3trade && !N3in)
      N3trade=false;
   if(N2trade && !N2in)
      N2trade=false;
   if(N1trade && !N1in)
      N1trade=false;



    //Condicion estudiada en cada tick despues de encontrar el pivote correctamente
   if(firstPivot)
     {
      //Declaramos tuplas de entornos del vwap y de las uñas para determinar entradas
      double vwapZone[2];
      double N5Zone[2];
      double N4Zone[2];
      double N3Zone[2];
      double N2Zone[2];
      double N1Zone[2];
      //Cota inferior del vwap +--Nota:10 es la conversion de Points per pip
      vwapZone[0]  = VWAP[1]-point*10*vwapZoneMultiplyer;
      //Cota superior del vwap
      vwapZone[1]  = VWAP[1]+point*10*vwapZoneMultiplyer;

      //Cota inferior de la uña 5
      N5Zone[0]    = N5[1]-point*10*vwapZoneMultiplyer;
      //Cota superior de la uña 5
      N5Zone[1]    = N5[1]+point*10*vwapZoneMultiplyer;

      //Cota inferior de la uña 4
      N4Zone[0]    = N4[1]-point*10*vwapZoneMultiplyer;
      //Cota superior de la uña 4
      N4Zone[1]    = N4[1]+point*10*vwapZoneMultiplyer;

      //Cota inferior de la uña 3
      N3Zone[0]    = N3[1]-point*10*vwapZoneMultiplyer;
      //Cota superior de la uña 3
      N3Zone[1]    = N3[1]+point*10*vwapZoneMultiplyer;

      //Cota inferior de la uña 2
      N2Zone[0]    = N2[1]-point*10*vwapZoneMultiplyer;
      //Cota superior de la uña 2
      N2Zone[1]    = N2[1]+point*10*vwapZoneMultiplyer;

      //Cota inferior de la uña 1
      N1Zone[0]    = N1[1]-point*10*vwapZoneMultiplyer;
      //Cota superior de la uña 1
      N1Zone[1]    = N1[1]+point*10*vwapZoneMultiplyer;



      double ask   = SymbolInfoDouble(_Symbol,SYMBOL_ASK);
      ask          = NormalizeDouble(ask,_Digits);

      double bid   = SymbolInfoDouble(_Symbol,SYMBOL_BID);
      bid          = NormalizeDouble(bid,_Digits);


      double distance  ;
      double lots      ;
      double riskAmount;




      datetime tm = TimeCurrent();

      MqlDateTime stm;
      TimeToStruct(tm,stm);

      MqlDateTime MyVwapTime;
      TimeToStruct(pivotTime,MyVwapTime);

      int openMinute            = MyVwapTime.min;
      int openHour              = MyVwapTime.hour;
      int openDayOfYear         = MyVwapTime.day_of_year;
      int openYear              = MyVwapTime.year;

      int localMinute           = stm.min;
      int localHour             = stm.hour;
      int localDayOfYear        = stm.day_of_year;
      int localYear             = stm.year;


      int Days                  = localDayOfYear-openDayOfYear;
      int Hours                 = localHour-openHour;
      int Minutes               = localMinute-openMinute;
      int year                  = localYear-openYear;
      int vwapTime              = year*365*24*60+Days*24*60+Hours*60+Minutes;

      double trueRiskPercentage = riskPercentage*(1-DynamicRiskAlpha(delta/6,vwapTime,option));
      Print("True Risk Percentage: ", trueRiskPercentage, " VWAP Time: ", vwapTime);

      if(Year!=stm.year)
        {
         Year=stm.year;
         EquityYear=totalEquityNow;
        }
      if(Month!=stm.mon)
        {
         Month=stm.mon;
         EquityMonth=totalEquityNow;
        }

      if(DayOfYear!=stm.day_of_year)
        {
         DayOfYear=stm.day_of_year;
         EquityDay=totalEquityNow;
        }




      bool overalCondition = overallPercent<maxDrowdown;
      bool YearCondition   =  yearPercent <= -maxDrowdownAnual  ;
      bool MonthCondition  =  monthPercent<= -maxDrowdownMonthly ;
      bool dayCondition    = dayPercent<= -maxDrowdownDaily; //dayPercent>=TargetDaily ||


      //N5
      //condicion de compra
      bool tradingHourCondition=!((21<=stm.hour) || (stm.hour<7));
      
      if(N5[1]!=0 && N5[1]!=EMPTY_VALUE && tradingHourCondition && iBarShift(_Symbol, Timeframe, pivotTime,true)>=switchCandelCondition && !YearCondition && !MonthCondition && !dayCondition)
        {
         if(AppPriceVWAP==PRICE_LOW)
           {
            distance          = ATR[1];
            double sl         = ask-distance*SlFactor;
            double slPoints   = distance*SlFactor/point;
            double tp         = ask+distance*TpFactor;

            sl                = NormalizeDouble(sl,_Digits);
            tp                = NormalizeDouble(tp,_Digits);
            riskAmount        = AccountInfoDouble(ACCOUNT_BALANCE)*trueRiskPercentage/100;
            lots              = Lots(_Symbol,riskAmount,slPoints);

            //N5
            if(ask<N5Zone[1] && ask>=N5[1] && !N5trade && !tradeO)
              {
               tradeO            = true;
               N5trade           = true;
               string comment    ="N5";
               tradeLots[4]      = lots;

               trade.Buy(lots,_Symbol,ask,sl,tp,comment);
               Print("Nuevo trade Buy en Nail: ", comment, " TrueRisk: ", trueRiskPercentage, "% RiskAmount: ", riskAmount, " ResultRetcode: ", trade.ResultRetcode(), " Result Deal: ", trade.ResultDeal(), " Pivot Time in minutes: ", vwapTime);
              }
            //N4
            if(ask<N4Zone[1] && ask>=N4[1] && !N4trade && !tradeO)
              {
               tradeO            = true;
               N4trade           = true;
               string comment    = "N4";
               tradeLots[3]      = lots;

               trade.Buy(lots,_Symbol,ask,sl,tp,comment);
               Print("Nuevo trade Buy en Nail: ", comment, " TrueRisk: ", trueRiskPercentage, "% RiskAmount: ", riskAmount, " ResultRetcode: ", trade.ResultRetcode(), " Result Deal: ", trade.ResultDeal(), " Pivot Time in minutes: ", vwapTime);
              }

            //N3
            if(ask<N3Zone[1] && ask>=N3[1] && !N3trade && !tradeO)
              {
               tradeO            = true;
               N3trade           = true;
               string comment    ="N3";
               tradeLots[2]      = lots;

               trade.Buy(lots,_Symbol,ask,sl,tp,comment);
               Print("Nuevo trade Buy en Nail: ", comment, " TrueRisk: ", trueRiskPercentage, "% RiskAmount: ", riskAmount, " ResultRetcode: ", trade.ResultRetcode(), " Result Deal: ", trade.ResultDeal(), " Pivot Time in minutes: ", vwapTime);
              }

            //N2
            if(ask<N2Zone[1] && ask>=N2[1] && !N2trade && !tradeO)
              {
               tradeO            =true;
               N2trade           =true;
               string comment    ="N2";
               tradeLots[1]      = lots;

               trade.Buy(lots,_Symbol,ask,sl,tp,comment);
               Print("Nuevo trade Buy en Nail: ", comment, " TrueRisk: ", trueRiskPercentage, "% RiskAmount: ", riskAmount, " ResultRetcode: ", trade.ResultRetcode(), " Result Deal: ", trade.ResultDeal(), " Pivot Time in minutes: ", vwapTime);
              }

            //N1
            if(ask<N1Zone[1] && ask>=N1[1] && !N1trade && !tradeO)
              {
               tradeO            = true;
               N1trade           = true;
               string comment    = "N1";
               tradeLots[0]      = lots;

               trade.Buy(lots,_Symbol,ask,sl,tp,comment);
               Print("Nuevo trade Buy en Nail: ", comment, " TrueRisk: ", trueRiskPercentage, "% RiskAmount: ", riskAmount, " ResultRetcode: ", trade.ResultRetcode(), " Result Deal: ", trade.ResultDeal(), " Pivot Time in minutes: ", vwapTime);
              }


           }
         //condicion de venta

         if(AppPriceVWAP==PRICE_HIGH)
           {


            distance          = ATR[1];

            double sl         =bid + distance*SlFactor;
            double slPoints   =distance*SlFactor/point;
            double tp         =bid-distance*TpFactor;

            riskAmount        =totalEquityNow*riskPercentage/100;
            lots              =Lots(_Symbol,riskAmount,slPoints);
            sl                =NormalizeDouble(sl,_Digits);
            tp                =NormalizeDouble(tp,_Digits);

            //N5
            if(bid<=N5[1] && bid>N5Zone[0] && !N5trade && !tradeO)
              {
               tradeO            =true;
               N5trade           =true;
               string comment    ="N5";
               tradeLots[4]      = lots;

               trade.Sell(lots,_Symbol,bid,sl,tp,comment);
               Print("Nuevo trade Buy en Nail: ", comment, " TrueRisk: ", riskPercentage, "% RiskAmount: ", riskAmount, " ResultRetcode: ", trade.ResultRetcode(), " Result Deal: ", trade.ResultDeal(), " Pivot Time in minutes: ", vwapTime);
              }
            //N4
            if(bid<=N4[1] && bid>N4Zone[0] && !N4trade && !tradeO)
              {
               tradeO            = true;
               N4trade           = true;
               string comment    ="N4";
               tradeLots[3]      = lots;

               trade.Sell(lots,_Symbol,bid,sl,tp,comment);
               Print("Nuevo trade Buy en Nail: ", comment, " TrueRisk: ", riskPercentage, "% RiskAmount: ", riskAmount, " ResultRetcode: ", trade.ResultRetcode(), " Result Deal: ", trade.ResultDeal(), " Pivot Time in minutes: ", vwapTime);
              }

            //N3

            if(bid<=N3[1] && bid>N3Zone[0] && !N3trade && !tradeO)
              {
               tradeO            = true;
               N3trade           = true;
               string comment    ="N3";
               tradeLots[2]      = lots;

               trade.Sell(lots,_Symbol,bid,sl,tp,comment);
               Print("Nuevo trade Buy en Nail: ", comment, " TrueRisk: ", riskPercentage, "% RiskAmount: ", riskAmount, " ResultRetcode: ", trade.ResultRetcode(), " Result Deal: ", trade.ResultDeal(), " Pivot Time in minutes: ", vwapTime);
              }
            //N2

            if(bid<=N2[1] && bid>N2Zone[0] && !N2trade && !tradeO)
              {
               tradeO            = true;
               N2trade           = true;
               string comment    ="N2";
               tradeLots[1]      = lots;

               trade.Sell(lots,_Symbol,bid,sl,tp,comment);
               Print("Nuevo trade Buy en Nail: ", comment, " TrueRisk: ", riskPercentage, "% RiskAmount: ", riskAmount, " ResultRetcode: ", trade.ResultRetcode(), " Result Deal: ", trade.ResultDeal(), " Pivot Time in minutes: ", vwapTime);
              }
            //N1

            if(bid<=N1[1] && bid>N1Zone[0] && !N1trade && !tradeO)
              {
               tradeO            = true;
               N1trade           = true;
               string comment    ="N1";
               tradeLots[0]      = lots;

               trade.Sell(lots,_Symbol,bid,sl,tp,comment);
               Print("Nuevo trade Buy en Nail: ", comment, " TrueRisk: ", riskPercentage, "% RiskAmount: ", riskAmount, " ResultRetcode: ", trade.ResultRetcode(), " Result Deal: ", trade.ResultDeal(), " Pivot Time in minutes: ", vwapTime);
              }
           }
        }
      ///CheckCloseTimer();
     }

  }




//+------------------------------------------------------------------+