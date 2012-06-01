package Elixys.JSON.Components
{
	import Elixys.Assets.Constants;
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ComponentTransfer extends ComponentBase
	{
		// Constructor
		public function ComponentTransfer(data:String = null, existingcontent:Object = null)
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
			return "TRANSFER";
		}
		public static function get SKINUP():Class
		{
			return tools_transfer_up;
		}
		public static function get SKINDOWN():Class
		{
			return tools_transfer_down;
		}
		public static function get SKINDISABLED():Class
		{
			return tools_transfer_disabled;
		}
		public static function get SKINACTIVE():Class
		{
			return tools_transfer_active;
		}

		// Static field details
		public static var FIELDCOUNT:int = 5;
		public static var FIELDLABELS:Array = [
			"SOURCE REACTOR", 
			"TARGET REACTOR", 
			"MODE", 
			"DURATION",
			"PRESSURE"
		];
		public static var FIELDTYPES:Array = [
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_DROPDOWN, 
			Constants.TYPE_INPUT, 
			Constants.TYPE_INPUT
		];
		public static var FIELDUNITS:Array = [
			"", 
			"", 
			"", 
			"SECONDS", 
			"PSI"
		];
		public static var FIELDPROPERTIES:Array = [
			"SourceReactor", 
			"TargetReactor", 
			"Mode", 
			"Duration",
			"Pressure"
		];
		
		// Data wrappers
		public function get SourceReactor():uint
		{
			return super.flash_proxy::getProperty("sourcereactor");
		}
		public function set SourceReactor(value:uint):void
		{
			super.flash_proxy::setProperty("sourcereactor", value);
		}

		public function get SourceReactorValidation():String
		{
			return super.flash_proxy::getProperty("sourcereactorvalidation");
		}

		public function get TargetReactor():uint
		{
			return super.flash_proxy::getProperty("targetreactor");
		}
		public function set TargetReactor(value:uint):void
		{
			super.flash_proxy::setProperty("targetreactor", value);
		}
		
		public function get TargetReactorValidation():String
		{
			return super.flash_proxy::getProperty("targetreactorvalidation");
		}

		public function get Mode():String
		{
			return super.flash_proxy::getProperty("mode");
		}
		public function set Mode(value:String):void
		{
			super.flash_proxy::setProperty("mode", value);
		}

		public function get ModeValidation():String
		{
			return super.flash_proxy::getProperty("modevalidation");
		}

		public function get Pressure():Number
		{
			return super.flash_proxy::getProperty("pressure");
		}
		public function set Pressure(value:Number):void
		{
			super.flash_proxy::setProperty("pressure", value);
		}
		
		public function get PressureValidation():String
		{
			return super.flash_proxy::getProperty("pressurevalidation");
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
		
		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sTransferDetails:String = JSONDataObject("sourcereactor", SourceReactor);
			sTransferDetails += JSONDataObject("targetreactor", TargetReactor);
			sTransferDetails += JSONDataString("mode", Mode);
			sTransferDetails += JSONDataObject("pressure", Pressure);
			sTransferDetails += JSONDataObject("duration", Duration, false);
			return sTransferDetails;
		}

		// Component comparison function.  Returns true if the components are equal, false otherwise.
		public static function CompareComponents(pComponentA:ComponentBase, pComponentB:ComponentBase):Boolean
		{
			var pComponentTransferA:ComponentTransfer = new ComponentTransfer(null, pComponentA);
			var pComponentTransferB:ComponentTransfer = new ComponentTransfer(null, pComponentB);
			if (pComponentTransferA.SourceReactor != pComponentTransferB.SourceReactor)
			{
				return false;
			}
			if (pComponentTransferA.TargetReactor != pComponentTransferB.TargetReactor)
			{
				return false;
			}
			if (pComponentTransferA.Mode != pComponentTransferB.Mode)
			{
				return false;
			}
			if (pComponentTransferA.Pressure != pComponentTransferB.Pressure)
			{
				return false;
			}
			if (pComponentTransferA.Duration != pComponentTransferB.Duration)
			{
				return false;
			}
			return true;
		}

		// Validates the transfer component
		public override function Validate():void
		{
			m_sSourceReactorError = ValidateField(SourceReactor, SourceReactorValidation);
			m_sTargetReactorError = ValidateField(TargetReactor, TargetReactorValidation);
			m_sModeError = ValidateField(Mode, ModeValidation);
			m_sPressureError = ValidateField(Pressure, PressureValidation);
			m_sDurationError = ValidateField(Duration, DurationValidation);
		}

		// Validation fields
		public function get SourceReactorError():String
		{
			return m_sSourceReactorError;
		}
		public function get TargetReactorError():String
		{
			return m_sTargetReactorError;
		}
		public function get ModeError():String
		{
			return m_sModeError;
		}
		public function get PressureError():String
		{
			return m_sPressureError;
		}
		public function get DurationError():String
		{
			return m_sDurationError;
		}
		
		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"TRANSFER\"," +
			"\"id\":0," +
			"\"note\":\"\"," +
			"\"sourcereactor\":0," +
			"\"targetreactor\":0," +
			"\"mode\":\"Trap\"," +
			"\"pressure\":0," +
			"\"duration\":0}";

		// Validation errors
		protected var m_sSourceReactorError:String = "";
		protected var m_sTargetReactorError:String = "";
		protected var m_sModeError:String = "";
		protected var m_sPressureError:String = "";
		protected var m_sDurationError:String = "";
	}
}
