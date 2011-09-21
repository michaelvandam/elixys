package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentTransfer extends Component
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
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Data wrappers
		public function get Reactor():uint
		{
			return super.flash_proxy::getProperty("reactor");
		}
		public function set Reactor(value:uint):void
		{
			super.flash_proxy::setProperty("reactor", value);
		}
		
		public function get ReactorDescription():String
		{
			return super.flash_proxy::getProperty("reactordescription");
		}
		
		public function get ReactorValidation():String
		{
			return super.flash_proxy::getProperty("reactorvalidation");
		}
		
		public function get TransferTarget():Reagent
		{
			if (m_pTarget == null)
			{
				m_pTarget = new Reagent(null, super.flash_proxy::getProperty("target"));
			}
			return m_pTarget;
		}
		public function set TransferTarget(value:Reagent):void
		{
			super.flash_proxy::setProperty("target", value);
			m_pTarget = null;
		}
		
		public function get TransferTargetDescription():String
		{
			return super.flash_proxy::getProperty("targetdescription");
		}
		
		public function get TransferTargetValidation():String
		{
			return super.flash_proxy::getProperty("targetvalidation");
		}

		// Format additional component details
		protected override function FormatComponentDetails():String
		{
			var sTransferDetails:String = JSONDataObject("reactor", Reactor);
			sTransferDetails += JSONDataObject("target", TransferTarget.ReagentID, false);
			return sTransferDetails;
		}

		// Type
		static public var TYPE:String = "TRANSFER";

		// State components
		private var m_pTarget:Reagent;

		// Default format
		static public var DEFAULT:String = "{" +
			"\"type\":\"component\"," +
			"\"componenttype\":\"TRANSFER\"," +
			"\"id\":0," +
			"\"name\":\"\"," +
			"\"reactor\":0," +
			"\"target\":" + Reagent.DEFAULT + "}";
	}
}
