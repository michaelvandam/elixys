package Elixys.JSON.Components
{
	import Elixys.Assets.Constants;
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentReact extends ComponentBase
	{
		// Constructor
		public function ComponentReact(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = DEFAULT;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != COMPONENTTYPE))
			{
				throw new Error("State object mismatch");
			}
		}
		
		// Static component type and skins
		public static function get COMPONENTTYPE():String
		{
			return "REACT";
		}
		public static function get SKINUP():Class
		{
			return tools_react_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_react_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_react_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_react_active;
		}

		// Static field details
		public static var FIELDCOUNT:int = 8;
		public static var FIELDLABELS:Array = [
			"REACTOR", 
			"DURATION", 
			"REACTION TEMP", 
			"FINAL TEMP",
			"COOLING DELAY", 
			"POSITION", 
			"STIR", 
			"STOP AT TEMP"
		];
		public static var FIELDTYPES:Array = [
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_INPUT, 
			Constants.TYPE_INPUT, 
			Constants.TYPE_INPUT,
			Constants.TYPE_INPUT, 
			Constants.TYPE_DROPDOWN,
			Constants.TYPE_CHECKBOXINPUT, 
			Constants.TYPE_CHECKBOX
		];
		public static var FIELDUNITS:Array = [
			"", 
			"SECONDS", 
			"CELSIUS", 
			"CELSIUS",
			"SECONDS", 
			"", 
			"", 
			""
		];
		public static var FIELDPROPERTIES:Array = [
			"Reactor", 
			"Duration", 
			"ReactionTemperature", 
			"FinalTemperature",
			"CoolingDelay", 
			"Position", 
			"Stir|StirSpeed", 
			"StopAtTemperature"
		];

		// Data wrappers
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		public function set Reactor(value:uint):void
		{
			super.flash_proxy::setProperty("reactor", value);
		}
		
		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
		}

		public function get Position():String
		{
			return super.flash_proxy::getProperty("position");
		}
		public function set Position(value:String):void
		{
			super.flash_proxy::setProperty("position", value);
		}

		public function get PositionValidation():String
		{
			return super.flash_proxy::getProperty("positionvalidation");
		}

		public function get Duration():uint
		{
			return super.flash_proxy::getProperty("duration");
		}
		public function set Duration(value:uint):void
		{
			super.flash_proxy::setProperty("duration", value);
		}

		public function get DurationValidation():String
		{
			return super.flash_proxy::getProperty("durationvalidation");
		}

		public function get ReactionTemperature():Number
		{
			return super.flash_proxy::getProperty("reactiontemperature");
		}
		public function set ReactionTemperature(value:Number):void
		{
			super.flash_proxy::setProperty("reactiontemperature", value);
		}
	
		public function get ReactionTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("reactiontemperaturevalidation");
		}
	
		public function get FinalTemperature():Number
		{
			return super.flash_proxy::getProperty("finaltemperature");
		}
		public function set FinalTemperature(value:Number):void
		{
			super.flash_proxy::setProperty("finaltemperature", value);
		}
	
		public function get FinalTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("finaltemperaturevalidation");
		}
	
		public function get CoolingDelay():uint
		{
			return super.flash_proxy::getProperty("coolingdelay");
		}
		public function set CoolingDelay(value:uint):void
		{
			super.flash_proxy::setProperty("coolingdelay", value);
		}
		
		public function get CoolingDelayValidation():String
		{
			return super.flash_proxy::getProperty("coolingdelayvalidation");
		}
		
		public function get Stir():uint
		{
			return super.flash_proxy::getProperty("stir");
		}
		public function set Stir(value:uint):void
		{
			super.flash_proxy::setProperty("stir", value);
		}
		
		public function get StirValidation():String
		{
			return super.flash_proxy::getProperty("stirvalidation");
		}

		public function get StirSpeed():uint
		{
			return super.flash_proxy::getProperty("stirspeed");
		}
		public function set StirSpeed(value:uint):void
		{
			super.flash_proxy::setProperty("stirspeed", value);
		}
	
		public function get StirSpeedValidation():String
		{
			return super.flash_proxy::getProperty("stirspeedvalidation");
		}

		public function get StopAtTemperature():uint
		{
			return super.flash_proxy::getProperty("stopattemperature");
		}
		public function set StopAtTemperature(value:uint):void
		{
			super.flash_proxy::setProperty("stopattemperature", value);
		}
		
		public function get StopAtTemperatureValidation():String
		{
			return super.flash_proxy::getProperty("stopattemperaturevalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sReactDetails:String = JSONDataObject("reactor", Reactor);
			sReactDetails += JSONDataObject("position", Position);
			sReactDetails += JSONDataObject("duration", Duration);
			sReactDetails += JSONDataObject("reactiontemperature", ReactionTemperature);
			sReactDetails += JSONDataObject("finaltemperature", FinalTemperature);
			sReactDetails += JSONDataObject("coolingdelay", CoolingDelay);
			sReactDetails += JSONDataObject("stir", Stir);
			sReactDetails += JSONDataObject("stirspeed", StirSpeed);
			sReactDetails += JSONDataObject("stopattemperature", StopAtTemperature, false);
			return sReactDetails;
		}
		
		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			var pComponentReactA:ComponentReact = new ComponentReact(null, pComponentA);
			var pComponentReactB:ComponentReact = new ComponentReact(null, pComponentB);
			if (pComponentReactA.Reactor != pComponentReactB.Reactor)
			{
				return false;
			}
			if (pComponentReactA.Position != pComponentReactB.Position)
			{
				return false;
			}
			if (pComponentReactA.Duration != pComponentReactB.Duration)
			{
				return false;
			}
			if (pComponentReactA.ReactionTemperature != pComponentReactB.ReactionTemperature)
			{
				return false;
			}
			if (pComponentReactA.FinalTemperature != pComponentReactB.FinalTemperature)
			{
				return false;
			}
			if (pComponentReactA.CoolingDelay != pComponentReactB.CoolingDelay)
			{
				return false;
			}
			if (pComponentReactA.Stir != pComponentReactB.Stir)
			{
				return false;
			}
			if (pComponentReactA.StirSpeed != pComponentReactB.StirSpeed)
			{
				return false;
			}
			if (pComponentReactA.StopAtTemperature != pComponentReactB.StopAtTemperature)
			{
				return false;
			}
			return true;
		}

		// Validates the transfer component
		public override function Validate():void
		{
			m_sReactorError = ValidateField(Reactor, ReactorValidation);
			m_sPositionError = ValidateField(Position, PositionValidation);
			m_sDurationError = ValidateField(Duration, DurationValidation);
			m_sReactionTemperatureError = ValidateField(ReactionTemperature, ReactionTemperatureValidation);
			m_sFinalTemperatureError = ValidateField(FinalTemperature, FinalTemperatureValidation);
			m_sCoolingDelayError = ValidateField(CoolingDelay, CoolingDelayValidation);
			m_sStirError = ValidateField(Stir, StirValidation);
			m_sStirSpeedError = ValidateField(StirSpeed, StirSpeedValidation);
			m_sStopAtTemperatureError = ValidateField(StopAtTemperature, StopAtTemperatureValidation);
		}
		
		// Validation fields
		public function get ReactorError():String
		{
			return m_sReactorError;
		}
		public function get PositionError():String
		{
			return m_sPositionError;
		}
		public function get DurationError():String
		{
			return m_sDurationError;
		}
		public function get ReactionTemperatureError():String
		{
			return m_sReactionTemperatureError;
		}
		public function get FinalTemperatureError():String
		{
			return m_sFinalTemperatureError;
		}
		public function get CoolingDelayError():String
		{
			return m_sCoolingDelayError;
		}
		public function get StirError():String
		{
			return m_sStirError;
		}
		public function get StirSpeedError():String
		{
			return m_sStirSpeedError;
		}
		public function get StopAtTemperatureError():String
		{
			return m_sStopAtTemperatureError;
		}
		
		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"REACT\"," +
			"\"id\":0," +
			"\"name\":\"React\"," +
			"\"reactor\":0," +
			"\"position\":0," +
			"\"duration\":0," +
			"\"reactiontemperature\":0," +
			"\"finaltemperature\":0," +
			"\"coolingdelay\":0," +
			"\"stir\":0}," +
			"\"stirspeed\":0}," +
			"\"stopattemperature\":0}";
		
		// Validation errors
		protected var m_sReactorError:String = "";
		protected var m_sPositionError:String = "";
		protected var m_sDurationError:String = "";
		protected var m_sReactionTemperatureError:String = "";
		protected var m_sFinalTemperatureError:String = "";
		protected var m_sCoolingDelayError:String = "";
		protected var m_sStirError:String = "";
		protected var m_sStirSpeedError:String = "";
		protected var m_sStopAtTemperatureError:String = "";
	}
}
