package Elixys.JSON.Components
{
	import Elixys.Assets.Constants;
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentMix extends ComponentBase
	{
		// Constructor
		public function ComponentMix(data:String = null, existingcontent:Object = null)
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
			return "MIX";
		}
		public static function get SKINUP():Class
		{
			return tools_mix_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_mix_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_mix_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_mix_active;
		}

		// Static field details
		public static var FIELDCOUNT:int = 3;
		public static var FIELDLABELS:Array = [
			"REACTOR", 
			"DURATION", 
			"STIR"
		];
		public static var FIELDTYPES:Array = [
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_INPUT, 
			Constants.TYPE_INPUT
		];
		public static var FIELDUNITS:Array = [
			"", 
			"SECONDS", 
			""
		];
		public static var FIELDPROPERTIES:Array = [
			"Reactor", 
			"MixTime", 
			"StirSpeed"
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
		
		public function get MixTime():uint
		{
			return super.flash_proxy::getProperty("mixtime");
		}
		public function set MixTime(value:uint):void
		{
			super.flash_proxy::setProperty("mixtime", value);
		}

		public function get MixTimeValidation():String
		{
			return super.flash_proxy::getProperty("mixtimevalidation");
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

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sMixDetails:String = JSONDataObject("reactor", Reactor);
			sMixDetails += JSONDataObject("mixtime", MixTime);
			sMixDetails += JSONDataObject("stirspeed", StirSpeed, false);
			return sMixDetails;
		}

		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			var pComponentMixA:ComponentMix = new ComponentMix(null, pComponentA);
			var pComponentMixB:ComponentMix = new ComponentMix(null, pComponentB);
			if (pComponentMixA.Reactor != pComponentMixB.Reactor)
			{
				return false;
			}
			if (pComponentMixA.MixTime != pComponentMixB.MixTime)
			{
				return false;
			}
			if (pComponentMixA.StirSpeed != pComponentMixB.StirSpeed)
			{
				return false;
			}
			return true;
		}

		// Validates the transfer component
		public override function Validate():void
		{
			m_sReactorError = ValidateField(Reactor, ReactorValidation);
			m_sMixTimeError = ValidateField(MixTime, MixTimeValidation);
			m_sStirSpeedError = ValidateField(StirSpeed, StirSpeedValidation);
		}
		
		// Validation fields
		public function get ReactorError():String
		{
			return m_sReactorError;
		}
		public function get MixTimeError():String
		{
			return m_sMixTimeError;
		}
		public function get StirSpeedError():String
		{
			return m_sStirSpeedError;
		}
		
		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"MIX\"," +
			"\"id\":0," +
			"\"note\":\"\"," +
			"\"reactor\":0," +
			"\"mixtime\":0," + 
			"\"stirspeed\":0}";
		
		// Validation errors
		protected var m_sReactorError:String = "";
		protected var m_sMixTimeError:String = "";
		protected var m_sStirSpeedError:String = "";
	}
}
